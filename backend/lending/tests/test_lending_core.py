from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import Account, CustomUser
from lending.models import CreditAssessment, Lender, LoanApplication, LoanOffer
from lending.services.credit_decision import CreditDecisionService
from lending.services.credit_features import CreditFeatureService
from lending.services.credit_scoring import CreditScoringService
from lending.services.emi import EMICalculationService
from lending.services.lender_matching import LenderMatchingService
from lending.services.offer_ranking import OfferRankingService


class LendingCoreTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="lenderuser",
            email="lenderuser@example.com",
            password="Demo@12345",
        )
        self.account = Account.objects.create(
            user=self.user,
            account_number="1234567890",
            balance=Decimal("250000.0000"),
            currency="INR",
            status="active",
        )

    def test_loan_application_creation(self):
        application = LoanApplication.objects.create(
            user=self.user,
            requested_amount=Decimal("200000.00"),
            requested_tenure_months=24,
            purpose=LoanApplication.PURPOSE_PERSONAL,
        )
        self.assertEqual(application.status, LoanApplication.STATUS_DRAFT)
        self.assertEqual(application.user, self.user)

    def test_credit_feature_service_handles_empty_history(self):
        features = CreditFeatureService.get_features(self.user)
        self.assertEqual(features["monthly_income"], Decimal("0.00"))
        self.assertEqual(features["transaction_count"], 0)

    def test_credit_scoring_returns_0_to_100_score(self):
        features = {
            "monthly_income": Decimal("60000.00"),
            "expense_to_income_ratio": Decimal("0.30"),
            "average_balance": Decimal("120000.00"),
            "transaction_count": 12,
            "transaction_stability": 0.75,
            "account_age_months": 12,
        }
        result = CreditScoringService.score(features)
        self.assertTrue(0 <= result["credit_score"] <= 100)
        self.assertIn(result["risk_category"], ["LOW", "MEDIUM", "HIGH", "VERY_HIGH"])

    def test_lender_matching_filters_eligible_lenders(self):
        Lender.objects.create(
            name="Alpha",
            minimum_credit_score=650,
            maximum_loan_amount=Decimal("100000.00"),
            minimum_loan_amount=Decimal("20000.00"),
            minimum_interest_rate=Decimal("12.50"),
            maximum_interest_rate=Decimal("18.00"),
            minimum_tenure_months=12,
            maximum_tenure_months=36,
            active=True,
        )
        Lender.objects.create(
            name="Beta",
            minimum_credit_score=700,
            maximum_loan_amount=Decimal("500000.00"),
            minimum_loan_amount=Decimal("25000.00"),
            minimum_interest_rate=Decimal("11.00"),
            maximum_interest_rate=Decimal("15.00"),
            minimum_tenure_months=12,
            maximum_tenure_months=60,
            active=True,
        )
        eligible = LenderMatchingService.match(720, Decimal("200000.00"), 24, Lender.objects.filter(active=True))
        self.assertEqual(len(eligible), 1)
        self.assertEqual(eligible[0].name, "Beta")

    def test_offer_ranking_returns_sorted_results(self):
        lenders = [
            Lender(name="A", minimum_credit_score=600, maximum_loan_amount=Decimal("100000.00"), minimum_loan_amount=Decimal("10000.00"), minimum_interest_rate=Decimal("12.00"), maximum_interest_rate=Decimal("15.00"), minimum_tenure_months=12, maximum_tenure_months=36, active=True),
            Lender(name="B", minimum_credit_score=700, maximum_loan_amount=Decimal("500000.00"), minimum_loan_amount=Decimal("10000.00"), minimum_interest_rate=Decimal("10.00"), maximum_interest_rate=Decimal("14.00"), minimum_tenure_months=12, maximum_tenure_months=48, active=True),
        ]
        ranked = OfferRankingService.rank(lenders, 720, 200000, 24)
        self.assertEqual(ranked[0]["lender"].name, "B")

    def test_emi_calculation_zero_interest(self):
        result = EMICalculationService.calculate(Decimal("120000.00"), Decimal("0.00"), 12)
        self.assertEqual(result["emi"], Decimal("10000.00"))
        self.assertEqual(result["total_repayment"], Decimal("120000.00"))

    def test_user_cannot_access_other_users_loan_data(self):
        other_user = CustomUser.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="Demo@12345",
        )
        Account.objects.create(
            user=other_user,
            account_number="2234567890",
            balance=Decimal("150000.0000"),
            currency="INR",
            status="active",
        )

        application = LoanApplication.objects.create(
            user=self.user,
            requested_amount=Decimal("200000.00"),
            requested_tenure_months=24,
            purpose=LoanApplication.PURPOSE_PERSONAL,
        )
        lender = Lender.objects.create(
            name="Crescent",
            minimum_credit_score=650,
            maximum_loan_amount=Decimal("500000.00"),
            minimum_loan_amount=Decimal("20000.00"),
            minimum_interest_rate=Decimal("10.50"),
            maximum_interest_rate=Decimal("14.50"),
            minimum_tenure_months=12,
            maximum_tenure_months=48,
            active=True,
        )
        offer = LoanOffer.objects.create(
            loan_application=application,
            lender=lender,
            loan_amount=Decimal("200000.00"),
            interest_rate=Decimal("10.50"),
            tenure_months=24,
            emi=Decimal("9206.12"),
            total_interest=Decimal("20000.00"),
            total_repayment=Decimal("220000.00"),
            offer_score=80,
            status=LoanOffer.STATUS_PENDING,
        )

        client = APIClient()
        client.force_authenticate(user=other_user)

        assessment_response = client.get(reverse("credit-assessment-detail", kwargs={"application_id": str(application.id)}))
        self.assertEqual(assessment_response.status_code, 403)

        accept_response = client.post(reverse("loan-offer-accept", kwargs={"pk": str(offer.id)}))
        self.assertEqual(accept_response.status_code, 403)

    def test_evaluate_persists_credit_decision_and_returns_it(self):
        application = LoanApplication.objects.create(
            user=self.user,
            requested_amount=Decimal("200000.00"),
            requested_tenure_months=24,
            purpose=LoanApplication.PURPOSE_PERSONAL,
            status=LoanApplication.STATUS_SUBMITTED,
        )
        Lender.objects.create(
            name="Integrated lender",
            minimum_credit_score=70,
            maximum_loan_amount=Decimal("500000.00"),
            minimum_loan_amount=Decimal("10000.00"),
            minimum_interest_rate=Decimal("10.00"),
            maximum_interest_rate=Decimal("15.00"),
            minimum_tenure_months=12,
            maximum_tenure_months=48,
        )
        features = {
            "monthly_income": Decimal("100000.00"),
            "monthly_expenses": Decimal("20000.00"),
            "average_balance": Decimal("200000.00"),
            "transaction_count": 20,
            "transaction_stability": 0.9,
            "income_stability": 0.9,
            "expense_to_income_ratio": Decimal("0.20"),
            "account_age_months": 12,
            "balance_volatility": Decimal("0.10"),
            "existing_debt": Decimal("0.00"),
            "repayment_behavior_score": 100,
        }
        client = APIClient()
        client.force_authenticate(user=self.user)

        with patch("lending.services.credit_decision.CreditFeatureService.get_features", return_value=features):
            response = client.post(reverse("loan-application-evaluate", kwargs={"pk": str(application.id)}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["decision"], CreditAssessment.DECISION_APPROVED)
        self.assertEqual(response.data["credit_decision"]["model_version"], CreditAssessment.MODEL_VERSION)
        self.assertTrue(CreditAssessment.objects.filter(loan_application=application).exists())
        self.assertEqual(LoanApplication.objects.get(id=application.id).status, LoanApplication.STATUS_APPROVED)

    def test_rejected_evaluation_does_not_create_offers(self):
        application = LoanApplication.objects.create(
            user=self.user,
            requested_amount=Decimal("200000.00"),
            requested_tenure_months=24,
            purpose=LoanApplication.PURPOSE_PERSONAL,
            status=LoanApplication.STATUS_SUBMITTED,
        )
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.post(reverse("loan-application-evaluate", kwargs={"pk": str(application.id)}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["decision"], CreditAssessment.DECISION_REJECTED)
        self.assertEqual(response.data["offers"], [])
        self.assertEqual(application.loan_offers.count(), 0)
        self.assertEqual(LoanApplication.objects.get(id=application.id).status, LoanApplication.STATUS_REJECTED)

    def test_cde_failure_falls_back_to_manual_review(self):
        application = LoanApplication.objects.create(
            user=self.user,
            requested_amount=Decimal("200000.00"),
            requested_tenure_months=24,
            purpose=LoanApplication.PURPOSE_PERSONAL,
            status=LoanApplication.STATUS_SUBMITTED,
        )
        client = APIClient()
        client.force_authenticate(user=self.user)

        with patch.object(CreditDecisionService, "assess_and_persist", side_effect=RuntimeError("engine unavailable")):
            response = client.post(reverse("loan-application-evaluate", kwargs={"pk": str(application.id)}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["decision"], CreditAssessment.DECISION_MANUAL_REVIEW)
        self.assertEqual(response.data["offers"], [])
        self.assertEqual(CreditAssessment.objects.get(loan_application=application).decision, CreditAssessment.DECISION_MANUAL_REVIEW)
