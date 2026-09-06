import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from accounts.models import CustomUser


class LoanApplication(models.Model):
    STATUS_DRAFT = "DRAFT"
    STATUS_SUBMITTED = "SUBMITTED"
    STATUS_UNDER_REVIEW = "UNDER_REVIEW"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_DISBURSED = "DISBURSED"
    STATUS_CLOSED = "CLOSED"

    STATUS_CHOICES = (
        (STATUS_DRAFT, "Draft"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_UNDER_REVIEW, "Under Review"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_DISBURSED, "Disbursed"),
        (STATUS_CLOSED, "Closed"),
    )

    PURPOSE_PERSONAL = "PERSONAL"
    PURPOSE_HOME = "HOME"
    PURPOSE_AUTO = "AUTO"
    PURPOSE_EDUCATION = "EDUCATION"
    PURPOSE_BUSINESS = "BUSINESS"

    PURPOSE_CHOICES = (
        (PURPOSE_PERSONAL, "Personal"),
        (PURPOSE_HOME, "Home"),
        (PURPOSE_AUTO, "Auto"),
        (PURPOSE_EDUCATION, "Education"),
        (PURPOSE_BUSINESS, "Business"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="loan_applications")
    requested_amount = models.DecimalField(max_digits=19, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    requested_tenure_months = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, default=PURPOSE_PERSONAL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "loan_applications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.requested_amount} ({self.status})"


class Lender(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    minimum_credit_score = models.PositiveIntegerField(default=0)
    maximum_loan_amount = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    minimum_loan_amount = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    minimum_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    maximum_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    minimum_tenure_months = models.PositiveIntegerField(default=12)
    maximum_tenure_months = models.PositiveIntegerField(default=60)
    active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "lenders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["active", "-created_at"]),
            models.Index(fields=["minimum_credit_score", "maximum_loan_amount"]),
        ]

    def __str__(self):
        return self.name


class CreditAssessment(models.Model):
    MODEL_VERSION = "rules-v1"

    RISK_LOW = "LOW"
    RISK_MEDIUM = "MEDIUM"
    RISK_HIGH = "HIGH"
    RISK_VERY_HIGH = "VERY_HIGH"

    RISK_CHOICES = (
        (RISK_LOW, "Low"),
        (RISK_MEDIUM, "Medium"),
        (RISK_HIGH, "High"),
        (RISK_VERY_HIGH, "Very High"),
    )

    DECISION_APPROVED = "APPROVED"
    DECISION_REJECTED = "REJECTED"
    DECISION_MANUAL_REVIEW = "MANUAL_REVIEW"
    DECISION_CHOICES = (
        (DECISION_APPROVED, "Approved"),
        (DECISION_REJECTED, "Rejected"),
        (DECISION_MANUAL_REVIEW, "Manual review"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="credit_assessments")
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name="credit_assessments")
    credit_score = models.PositiveIntegerField(default=0)
    risk_category = models.CharField(max_length=20, choices=RISK_CHOICES, default=RISK_MEDIUM)
    income_score = models.PositiveIntegerField(default=0)
    expense_score = models.PositiveIntegerField(default=0)
    balance_score = models.PositiveIntegerField(default=0)
    transaction_score = models.PositiveIntegerField(default=0)
    repayment_score = models.PositiveIntegerField(default=0)
    debt_score = models.PositiveIntegerField(default=0)
    maximum_eligible_amount = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    eligibility = models.BooleanField(default=False)
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES, default=DECISION_REJECTED)
    reasons = models.JSONField(default=list, blank=True)
    risk_factors = models.JSONField(default=list, blank=True)
    model_version = models.CharField(max_length=50, default=MODEL_VERSION)
    input_snapshot = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "credit_assessments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["loan_application", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.credit_score} ({self.risk_category})"


class LoanOffer(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_ACCEPTED = "ACCEPTED"
    STATUS_REJECTED = "REJECTED"
    STATUS_EXPIRED = "EXPIRED"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_EXPIRED, "Expired"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name="loan_offers")
    lender = models.ForeignKey(Lender, on_delete=models.PROTECT, related_name="loan_offers")
    loan_amount = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    tenure_months = models.PositiveIntegerField(default=12)
    emi = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    total_interest = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    total_repayment = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    offer_score = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "loan_offers"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["loan_application", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.lender.name} - {self.loan_amount}"


class Loan(models.Model):
    STATUS_ACTIVE = "ACTIVE"
    STATUS_CLOSED = "CLOSED"
    STATUS_DEFAULTED = "DEFAULTED"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_CLOSED, "Closed"),
        (STATUS_DEFAULTED, "Defaulted"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name="loans")
    lender = models.ForeignKey(Lender, on_delete=models.PROTECT, related_name="loans")
    principal_amount = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    tenure_months = models.PositiveIntegerField(default=12)
    emi = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    total_interest = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    total_repayment = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE, db_index=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "loans"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["loan_application", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"Loan {self.id} - {self.principal_amount}"


class Repayment(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_PAID = "PAID"
    STATUS_PARTIAL = "PARTIAL"
    STATUS_OVERDUE = "OVERDUE"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_PARTIAL, "Partial"),
        (STATUS_OVERDUE, "Overdue"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="repayments")
    installment_number = models.PositiveIntegerField(default=1)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    paid_amount = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "repayments"
        ordering = ["installment_number"]
        indexes = [
            models.Index(fields=["loan", "due_date"]),
            models.Index(fields=["status", "due_date"]),
            models.Index(fields=["loan", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.loan_id} - Installment {self.installment_number}"
