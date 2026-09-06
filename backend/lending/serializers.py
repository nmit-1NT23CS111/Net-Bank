from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from accounts.models import Account

from .models import CreditAssessment, Loan, LoanApplication, LoanOffer, Lender, Repayment


class LoanApplicationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = LoanApplication
        fields = (
            "id",
            "user",
            "requested_amount",
            "requested_tenure_months",
            "purpose",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "status", "created_at", "updated_at")

    def validate_requested_amount(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("Requested amount must be greater than zero.")
        if value > Decimal("10000000.00"):
            raise serializers.ValidationError("Requested amount exceeds the maximum demo threshold.")
        return value

    def validate_requested_tenure_months(self, value):
        if value <= 0:
            raise serializers.ValidationError("Tenure must be greater than zero.")
        if value > 360:
            raise serializers.ValidationError("Tenure exceeds the allowed maximum.")
        return value

    def validate(self, attrs):
        if not Account.objects.filter(user=self.context["request"].user, status="active").exists():
            raise serializers.ValidationError({"detail": "User must have an active account to apply for a loan."})
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class CreditAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditAssessment
        fields = (
            "id",
            "user",
            "loan_application",
            "credit_score",
            "risk_category",
            "income_score",
            "expense_score",
            "balance_score",
            "transaction_score",
            "repayment_score",
            "debt_score",
            "maximum_eligible_amount",
            "eligibility",
            "decision",
            "reasons",
            "risk_factors",
            "model_version",
            "input_snapshot",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class LenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lender
        fields = (
            "id",
            "name",
            "minimum_credit_score",
            "maximum_loan_amount",
            "minimum_loan_amount",
            "minimum_interest_rate",
            "maximum_interest_rate",
            "minimum_tenure_months",
            "maximum_tenure_months",
            "active",
            "created_at",
        )
        read_only_fields = fields


class LoanOfferSerializer(serializers.ModelSerializer):
    lender = LenderSerializer(read_only=True)

    class Meta:
        model = LoanOffer
        fields = (
            "id",
            "loan_application",
            "lender",
            "loan_amount",
            "interest_rate",
            "tenure_months",
            "emi",
            "total_interest",
            "total_repayment",
            "offer_score",
            "status",
            "expires_at",
            "created_at",
        )
        read_only_fields = fields


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = (
            "id",
            "loan_application",
            "lender",
            "principal_amount",
            "interest_rate",
            "tenure_months",
            "emi",
            "total_interest",
            "total_repayment",
            "status",
            "disbursed_at",
            "created_at",
        )
        read_only_fields = fields


class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment
        fields = (
            "id",
            "loan",
            "installment_number",
            "due_date",
            "amount",
            "paid_amount",
            "status",
            "paid_at",
            "created_at",
        )
        read_only_fields = fields


class RepaymentPaymentSerializer(serializers.Serializer):
    payment_amount = serializers.DecimalField(max_digits=19, decimal_places=2, min_value=Decimal("0.01"))

    def validate(self, attrs):
        repayment = self.context["repayment"]
        if repayment.status in (Repayment.STATUS_PAID, Repayment.STATUS_OVERDUE):
            raise serializers.ValidationError({"detail": "This installment is no longer payable."})
        if attrs["payment_amount"] > repayment.amount:
            raise serializers.ValidationError({"detail": "Payment cannot exceed installment amount."})
        return attrs
