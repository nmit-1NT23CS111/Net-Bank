from decimal import Decimal

from ..models import CreditAssessment
from .credit_features import CreditFeatureService
from .credit_scoring import CreditScoringService


class CreditDecisionService:
    MODEL_VERSION = CreditAssessment.MODEL_VERSION

    @staticmethod
    def assess(user, loan_application, features=None):
        features = features or CreditFeatureService.get_features(user)
        scoring = CreditScoringService.score(features)
        credit_score = scoring["credit_score"]
        risk_category = scoring["risk_category"]

        maximum_eligible_amount = Decimal("0.00")
        monthly_income = features.get("monthly_income", Decimal("0.00"))
        if monthly_income > 0:
            maximum_eligible_amount = monthly_income * Decimal("6")

        if risk_category == "LOW":
            adjustment = Decimal("1.00")
        elif risk_category == "MEDIUM":
            adjustment = Decimal("0.85")
        elif risk_category == "HIGH":
            adjustment = Decimal("0.65")
        else:
            adjustment = Decimal("0.50")
        maximum_eligible_amount = max(Decimal("0.00"), maximum_eligible_amount * adjustment)

        eligible = credit_score >= 50 and loan_application.requested_amount <= maximum_eligible_amount
        decision = "APPROVED" if eligible else "REJECTED"

        reasons = []
        risk_factors = []

        if features.get("monthly_income", Decimal("0.00")) > 0:
            reasons.append("Stable income profile")
        if features.get("average_balance", Decimal("0.00")) > Decimal("50000"):
            reasons.append("Healthy average account balance")
        if features.get("transaction_count", 0) >= 10:
            reasons.append("Consistent transaction activity")
        if features.get("expense_to_income_ratio", Decimal("0.00")) > Decimal("0.60"):
            risk_factors.append("Expense-to-income ratio is elevated")
        if features.get("account_age_months", 0) <= 2:
            risk_factors.append("Account history is still limited")
        if not reasons:
            reasons.append("Insufficient historical data for a strong positive signal")
        if not risk_factors:
            risk_factors.append("No material risk flags detected")

        return {
            "credit_score": credit_score,
            "risk_category": risk_category,
            "eligible": eligible,
            "maximum_eligible_amount": maximum_eligible_amount,
            "decision": decision,
            "reasons": reasons,
            "risk_factors": risk_factors,
            "component_scores": scoring["component_scores"],
        }

    @staticmethod
    def _json_safe_features(features):
        return {
            key: str(value) if isinstance(value, Decimal) else value
            for key, value in features.items()
        }

    @classmethod
    def persist_assessment(cls, user, loan_application, decision, features):
        component_scores = decision["component_scores"]
        return CreditAssessment.objects.create(
            user=user,
            loan_application=loan_application,
            credit_score=decision["credit_score"],
            risk_category=decision["risk_category"],
            income_score=component_scores["income_score"],
            expense_score=component_scores["expense_score"],
            balance_score=component_scores["balance_score"],
            transaction_score=component_scores["transaction_score"],
            repayment_score=features.get("repayment_behavior_score", 0),
            debt_score=component_scores["debt_score"],
            maximum_eligible_amount=decision["maximum_eligible_amount"],
            eligibility=decision["eligible"],
            decision=decision["decision"],
            reasons=decision["reasons"],
            risk_factors=decision["risk_factors"],
            model_version=cls.MODEL_VERSION,
            input_snapshot=cls._json_safe_features(features),
        )

    @classmethod
    def assess_and_persist(cls, user, loan_application):
        features = CreditFeatureService.get_features(user)
        decision = cls.assess(user, loan_application, features=features)
        return cls.persist_assessment(user, loan_application, decision, features)

    @classmethod
    def manual_review(cls, user, loan_application, reason):
        return CreditAssessment.objects.create(
            user=user,
            loan_application=loan_application,
            risk_category=CreditAssessment.RISK_MEDIUM,
            decision=CreditAssessment.DECISION_MANUAL_REVIEW,
            reasons=["Credit assessment requires manual review."],
            risk_factors=[reason],
            model_version=cls.MODEL_VERSION,
        )
