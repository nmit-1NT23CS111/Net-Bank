from django.urls import path

from .views import (
    CreditAssessmentView,
    LenderViewSet,
    LoanApplicationViewSet,
    LoanOfferViewSet,
    LoanViewSet,
    RepaymentViewSet,
)

urlpatterns = [
    path("applications/", LoanApplicationViewSet.as_view({"get": "list", "post": "create"}), name="loan-applications"),
    path("applications/<uuid:pk>/", LoanApplicationViewSet.as_view({"get": "retrieve"}), name="loan-application-detail"),
    path("applications/<uuid:pk>/submit/", LoanApplicationViewSet.as_view({"post": "submit"}), name="loan-application-submit"),
    path("applications/<uuid:pk>/evaluate/", LoanApplicationViewSet.as_view({"post": "evaluate"}), name="loan-application-evaluate"),
    path("credit/assess/", CreditAssessmentView.as_view(), name="credit-assess"),
    path("lenders/", LenderViewSet.as_view({"get": "list"}), name="lenders"),
    path("offers/<uuid:pk>/accept/", LoanOfferViewSet.as_view({"post": "accept"}), name="loan-offer-accept"),
    path("loans/", LoanViewSet.as_view({"get": "list"}), name="loans"),
    path("loans/<uuid:pk>/", LoanViewSet.as_view({"get": "retrieve"}), name="loan-detail"),
    path("loans/<uuid:loan_id>/repayments/", RepaymentViewSet.as_view({"get": "list"}), name="loan-repayments"),
    path("repayments/<uuid:pk>/pay/", RepaymentViewSet.as_view({"post": "pay"}), name="repayment-pay"),
]
