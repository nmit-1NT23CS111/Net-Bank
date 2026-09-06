from datetime import timedelta
from decimal import Decimal
import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets, views
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import Account
from transactions.models import AuditLog

from .models import CreditAssessment, Lender, Loan, LoanApplication, LoanOffer, Repayment
from .serializers import (
    CreditAssessmentSerializer,
    LenderSerializer,
    LoanApplicationSerializer,
    LoanOfferSerializer,
    LoanSerializer,
    RepaymentPaymentSerializer,
    RepaymentSerializer,
)
from .services.credit_decision import CreditDecisionService
from .services.emi import EMICalculationService
from .services.lender_matching import LenderMatchingService
from .services.offer_ranking import OfferRankingService
from .services.repayment import RepaymentScheduleService, RepaymentProcessingService

logger = logging.getLogger(__name__)


class LoanApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LoanApplication.objects.filter(user=self.request.user).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        app = serializer.save()
        return Response({"success": True, "application": LoanApplicationSerializer(app, context={"request": request}).data}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        application = self.get_object()
        if application.status != LoanApplication.STATUS_DRAFT:
            return Response({"success": False, "detail": "Application can only be submitted from DRAFT status."}, status=status.HTTP_400_BAD_REQUEST)
        application.status = LoanApplication.STATUS_SUBMITTED
        application.save(update_fields=["status", "updated_at"])
        return Response({"success": True, "application": LoanApplicationSerializer(application, context={"request": request}).data})

    @action(detail=True, methods=["post"], url_path="evaluate")
    def evaluate(self, request, pk=None):
        application = self.get_object()
        if application.status not in [LoanApplication.STATUS_SUBMITTED, LoanApplication.STATUS_UNDER_REVIEW]:
            return Response({"success": False, "detail": "Application must be submitted before evaluation."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                assessment = CreditDecisionService.assess_and_persist(request.user, application)
                application.status = {
                    CreditAssessment.DECISION_APPROVED: LoanApplication.STATUS_APPROVED,
                    CreditAssessment.DECISION_REJECTED: LoanApplication.STATUS_REJECTED,
                }.get(assessment.decision, LoanApplication.STATUS_UNDER_REVIEW)
                application.save(update_fields=["status", "updated_at"])
                AuditLog.objects.create(
                    user=request.user,
                    action="credit_decision",
                    resource_type="credit_assessment",
                    resource_id=str(assessment.id),
                    new_values={"decision": assessment.decision, "credit_score": assessment.credit_score},
                    ip_address=request.META.get("REMOTE_ADDR") or "0.0.0.0",
                )

                offers = []
                if assessment.decision == CreditAssessment.DECISION_APPROVED:
                    lenders = Lender.objects.filter(active=True)
                    matched = LenderMatchingService.match(assessment.credit_score, application.requested_amount, application.requested_tenure_months, lenders)
                    ranked = OfferRankingService.rank(matched, assessment.credit_score, application.requested_amount, application.requested_tenure_months)
                    for item in ranked:
                        lender = item["lender"]
                        emi_data = EMICalculationService.calculate(application.requested_amount, lender.minimum_interest_rate, application.requested_tenure_months)
                        offer = LoanOffer.objects.create(
                            loan_application=application,
                            lender=lender,
                            loan_amount=application.requested_amount,
                            interest_rate=lender.minimum_interest_rate,
                            tenure_months=application.requested_tenure_months,
                            emi=emi_data["emi"],
                            total_interest=emi_data["total_interest"],
                            total_repayment=emi_data["total_repayment"],
                            offer_score=item["offer_score"],
                            expires_at=timezone.now() + timedelta(hours=24),
                        )
                        offers.append(LoanOfferSerializer(offer).data)
        except Exception:
            logger.exception("Credit assessment failed for loan application %s", application.id)
            with transaction.atomic():
                assessment = CreditDecisionService.manual_review(request.user, application, "Assessment service unavailable.")
                application.status = LoanApplication.STATUS_UNDER_REVIEW
                application.save(update_fields=["status", "updated_at"])
                AuditLog.objects.create(
                    user=request.user,
                    action="credit_decision",
                    resource_type="credit_assessment",
                    resource_id=str(assessment.id),
                    new_values={"decision": assessment.decision, "credit_score": assessment.credit_score},
                    ip_address=request.META.get("REMOTE_ADDR") or "0.0.0.0",
                    status="manual_review",
                )
            offers = []

        return Response({
            "success": True,
            "application_id": str(application.id),
            "application": LoanApplicationSerializer(application, context={"request": request}).data,
            "credit_score": assessment.credit_score,
            "risk_category": assessment.risk_category,
            "eligible": assessment.eligibility,
            "maximum_eligible_amount": str(assessment.maximum_eligible_amount),
            "decision": assessment.decision,
            "reasons": assessment.reasons,
            "risk_factors": assessment.risk_factors,
            "assessment": CreditAssessmentSerializer(assessment).data,
            "credit_decision": CreditAssessmentSerializer(assessment).data,
            "offers": offers,
        })


class CreditAssessmentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, application_id=None):
        if application_id is None:
            return Response({"success": False, "detail": "Application ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        application = get_object_or_404(LoanApplication, id=application_id)
        if application.user != request.user:
            return Response({"success": False, "detail": "You do not own this application."}, status=status.HTTP_403_FORBIDDEN)

        assessment = CreditAssessment.objects.filter(loan_application=application).order_by("-created_at").first()
        if assessment is None:
            return Response({"success": False, "detail": "No credit assessment found for this application."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "assessment": CreditAssessmentSerializer(assessment).data}, status=status.HTTP_200_OK)

    def post(self, request):
        loan_id = request.data.get("loan_application_id")
        application = get_object_or_404(LoanApplication, id=loan_id)
        if application.user != request.user:
            return Response({"success": False, "detail": "You do not own this application."}, status=status.HTTP_403_FORBIDDEN)

        assessment = CreditDecisionService.assess_and_persist(request.user, application)
        application.status = LoanApplication.STATUS_UNDER_REVIEW
        application.save(update_fields=["status", "updated_at"])
        return Response({"success": True, "assessment": CreditAssessmentSerializer(assessment).data}, status=status.HTTP_201_CREATED)


class LenderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lender.objects.filter(active=True)
    serializer_class = LenderSerializer
    permission_classes = [permissions.IsAuthenticated]


class LoanOfferViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LoanOffer.objects.all().select_related("lender", "loan_application")
    serializer_class = LoanOfferSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"], url_path="accept")
    def accept(self, request, pk=None):
        offer = get_object_or_404(LoanOffer, id=pk)
        if offer.loan_application.user != request.user:
            return Response({"success": False, "detail": "You do not own this offer."}, status=status.HTTP_403_FORBIDDEN)
        if offer.loan_application.status != LoanApplication.STATUS_APPROVED:
            return Response({"success": False, "detail": "Only approved applications can be disbursed."}, status=status.HTTP_400_BAD_REQUEST)
        if offer.status != LoanOffer.STATUS_PENDING:
            return Response({"success": False, "detail": "This offer is no longer valid."}, status=status.HTTP_400_BAD_REQUEST)
        if offer.expires_at and offer.expires_at < timezone.now():
            offer.status = LoanOffer.STATUS_EXPIRED
            offer.save(update_fields=["status"])
            return Response({"success": False, "detail": "This offer has expired."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            existing_loan = Loan.objects.filter(loan_application=offer.loan_application).first()
            if existing_loan is not None:
                return Response({"success": False, "detail": "A loan already exists for this application."}, status=status.HTTP_400_BAD_REQUEST)

            emi_data = EMICalculationService.calculate(offer.loan_amount, offer.interest_rate, offer.tenure_months)
            loan = Loan.objects.create(
                loan_application=offer.loan_application,
                lender=offer.lender,
                principal_amount=offer.loan_amount,
                interest_rate=offer.interest_rate,
                tenure_months=offer.tenure_months,
                emi=emi_data["emi"],
                total_interest=emi_data["total_interest"],
                total_repayment=emi_data["total_repayment"],
                status=Loan.STATUS_ACTIVE,
                disbursed_at=timezone.now(),
            )

            offer.status = LoanOffer.STATUS_ACCEPTED
            offer.save(update_fields=["status"])
            LoanOffer.objects.filter(loan_application=offer.loan_application).exclude(id=offer.id).update(status=LoanOffer.STATUS_REJECTED)
            offer.loan_application.status = LoanApplication.STATUS_DISBURSED
            offer.loan_application.save(update_fields=["status", "updated_at"])

            RepaymentScheduleService.generate(loan)

            return Response({"success": True, "loan": LoanSerializer(loan).data}, status=status.HTTP_201_CREATED)


class LoanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.filter(loan_application__user=self.request.user).select_related("loan_application", "lender").order_by("-created_at")


class RepaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RepaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Repayment.objects.filter(loan__loan_application__user=self.request.user).select_related("loan").order_by("installment_number")

    def list(self, request, *args, **kwargs):
        loan_id = kwargs.get("loan_id")
        loan = get_object_or_404(Loan, id=loan_id, loan_application__user=request.user)
        repayments = Repayment.objects.filter(loan=loan).order_by("installment_number")
        return Response({"success": True, "results": RepaymentSerializer(repayments, many=True).data})

    @action(detail=True, methods=["post"], url_path="pay")
    def pay(self, request, pk=None):
        repayment = get_object_or_404(Repayment, id=pk)
        if repayment.loan.loan_application.user != request.user:
            return Response({"success": False, "detail": "You do not own this repayment."}, status=status.HTTP_403_FORBIDDEN)
        serializer = RepaymentPaymentSerializer(data=request.data, context={"repayment": repayment})
        serializer.is_valid(raise_exception=True)

        updated = RepaymentProcessingService.process(repayment, serializer.validated_data["payment_amount"])
        return Response({"success": True, "message": "Payment recorded successfully.", "repayment": RepaymentSerializer(updated).data})
