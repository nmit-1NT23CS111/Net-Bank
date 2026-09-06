from django.contrib import admin

from .models import CreditAssessment, Lender, Loan, LoanApplication, LoanOffer, Repayment


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "requested_amount", "requested_tenure_months", "purpose", "status", "created_at")
    list_filter = ("status", "purpose")
    search_fields = ("user__email", "purpose")


@admin.register(Lender)
class LenderAdmin(admin.ModelAdmin):
    list_display = ("name", "minimum_credit_score", "maximum_loan_amount", "minimum_interest_rate", "active")
    list_filter = ("active",)
    search_fields = ("name",)


@admin.register(CreditAssessment)
class CreditAssessmentAdmin(admin.ModelAdmin):
    list_display = ("user", "loan_application", "credit_score", "risk_category", "decision", "created_at")
    list_filter = ("risk_category", "decision")


@admin.register(LoanOffer)
class LoanOfferAdmin(admin.ModelAdmin):
    list_display = ("loan_application", "lender", "loan_amount", "interest_rate", "offer_score", "status")
    list_filter = ("status",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("loan_application", "lender", "principal_amount", "interest_rate", "tenure_months", "status")
    list_filter = ("status",)


@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ("loan", "installment_number", "due_date", "amount", "paid_amount", "status")
    list_filter = ("status",)
    search_fields = ("loan__loan_application__user__email",)
