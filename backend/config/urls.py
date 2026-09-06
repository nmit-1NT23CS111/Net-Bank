from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    AccountViewSet,
    ChangePasswordView,
    LoginView,
    UserProfileView,
    UserRegisterView,
    VerifyEmailView,
    ResendVerificationEmailView,
    ForgotPasswordView,
    ResetPasswordView,
    RequestOTPView,
    VerifyOTPView,
    GoogleOAuthCallbackView,
    LinkedOAuthProvidersView,
    UnlinkOAuthProviderView,
)
from core.views import DashboardSummaryView, HealthCheckView
from lending.views import CreditAssessmentView, LenderViewSet, LoanApplicationViewSet, LoanOfferViewSet, LoanViewSet, RepaymentViewSet
from transactions.views import AuditLogViewSet, DepositView, TransactionViewSet, TransferView, WithdrawalView


router = DefaultRouter()
router.register(r"accounts", AccountViewSet, basename="account")
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("", RedirectView.as_view(url="/api/v1/health/", permanent=False)),
    path("admin/", admin.site.urls),
    path(
        "api/v1/",
        include(
            [
                path("health/", HealthCheckView.as_view(), name="health"),
                # Auth endpoints
                path("auth/register/", UserRegisterView.as_view(), name="register"),
                path("auth/login/", LoginView.as_view(), name="login"),
                path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
                path("auth/verify-email/", VerifyEmailView.as_view(), name="verify-email"),
                path("auth/resend-verification-email/", ResendVerificationEmailView.as_view(), name="resend-verification-email"),
                path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
                path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),
                path("auth/request-otp/", RequestOTPView.as_view(), name="request-otp"),
                path("auth/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
                path("auth/google/callback/", GoogleOAuthCallbackView.as_view(), name="google-callback"),
                path("auth/oauth/providers/", LinkedOAuthProvidersView.as_view(), name="oauth-providers"),
                path("auth/oauth/unlink/", UnlinkOAuthProviderView.as_view(), name="unlink-oauth"),
                # User endpoints
                path("users/profile/", UserProfileView.as_view(), name="profile"),
                path("users/change-password/", ChangePasswordView.as_view(), name="change-password"),
                # Dashboard endpoint
                path("dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
                # Lending endpoints
                path("loans/applications/", LoanApplicationViewSet.as_view({"get": "list", "post": "create"}), name="loan-applications"),
                path("loans/applications/<uuid:pk>/", LoanApplicationViewSet.as_view({"get": "retrieve"}), name="loan-application-detail"),
                path("loans/applications/<uuid:pk>/submit/", LoanApplicationViewSet.as_view({"post": "submit"}), name="loan-application-submit"),
                path("loans/applications/<uuid:pk>/evaluate/", LoanApplicationViewSet.as_view({"post": "evaluate"}), name="loan-application-evaluate"),
                path("credit/assess/", CreditAssessmentView.as_view(), name="credit-assess"),
                path("credit/assessments/<uuid:application_id>/", CreditAssessmentView.as_view(), name="credit-assessment-detail"),
                path("lenders/", LenderViewSet.as_view({"get": "list"}), name="lenders"),
                path("loans/offers/<uuid:pk>/accept/", LoanOfferViewSet.as_view({"post": "accept"}), name="loan-offer-accept"),
                path("loans/", LoanViewSet.as_view({"get": "list"}), name="loans"),
                path("loans/<uuid:pk>/", LoanViewSet.as_view({"get": "retrieve"}), name="loan-detail"),
                path("loans/<uuid:loan_id>/repayments/", RepaymentViewSet.as_view({"get": "list"}), name="loan-repayments"),
                path("repayments/<uuid:pk>/pay/", RepaymentViewSet.as_view({"post": "pay"}), name="repayment-pay"),
                # Transaction endpoints
                path("transactions/deposit/", DepositView.as_view(), name="deposit"),
                path("transactions/withdraw/", WithdrawalView.as_view(), name="withdraw"),
                path("transactions/transfer/", TransferView.as_view(), name="transfer"),
                # Router endpoints
                path("", include(router.urls)),
            ]
        ),
    ),
]
