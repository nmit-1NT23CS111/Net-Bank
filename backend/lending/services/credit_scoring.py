from decimal import Decimal


class CreditScoringService:
    """Rule-based prototype credit score built from existing bank behaviour."""

    @staticmethod
    def score(features):
        income_score = CreditScoringService._score_income(features.get("monthly_income", Decimal("0.00")))
        expense_score = CreditScoringService._score_expense_ratio(features.get("expense_to_income_ratio", Decimal("0.00")))
        balance_score = CreditScoringService._score_balance(features.get("average_balance", Decimal("0.00")))
        transaction_score = CreditScoringService._score_transaction(features.get("transaction_count", 0), features.get("transaction_stability", 0.0))
        account_age_score = CreditScoringService._score_account_age(features.get("account_age_months", 0))
        debt_score = 100

        credit_score = (
            income_score * 0.25
            + expense_score * 0.20
            + balance_score * 0.20
            + transaction_score * 0.15
            + account_age_score * 0.10
            + debt_score * 0.10
        )

        credit_score = max(0, min(100, round(credit_score)))

        if credit_score >= 80:
            risk = "LOW"
        elif credit_score >= 65:
            risk = "MEDIUM"
        elif credit_score >= 50:
            risk = "HIGH"
        else:
            risk = "VERY_HIGH"

        return {
            "credit_score": int(credit_score),
            "risk_category": risk,
            "component_scores": {
                "income_score": int(income_score),
                "expense_score": int(expense_score),
                "balance_score": int(balance_score),
                "transaction_score": int(transaction_score),
                "account_age_score": int(account_age_score),
                "debt_score": int(debt_score),
            },
        }

    @staticmethod
    def _score_income(monthly_income):
        monthly_income = Decimal(str(monthly_income))
        if monthly_income <= 0:
            return 0
        if monthly_income < Decimal("20000"):
            return 35
        if monthly_income < Decimal("50000"):
            return 60
        if monthly_income < Decimal("100000"):
            return 80
        return 95

    @staticmethod
    def _score_expense_ratio(expense_ratio):
        ratio = Decimal(str(expense_ratio))
        if ratio <= 0:
            return 100
        if ratio < Decimal("0.20"):
            return 100
        if ratio < Decimal("0.40"):
            return 90
        if ratio < Decimal("0.60"):
            return 70
        if ratio < Decimal("0.80"):
            return 45
        return 20

    @staticmethod
    def _score_balance(average_balance):
        avg = Decimal(str(average_balance))
        if avg <= 0:
            return 20
        if avg < Decimal("10000"):
            return 25
        if avg < Decimal("50000"):
            return 45
        if avg < Decimal("150000"):
            return 70
        if avg < Decimal("500000"):
            return 90
        return 100

    @staticmethod
    def _score_transaction(transaction_count, stability):
        if transaction_count < 5:
            score = 25
        elif transaction_count < 10:
            score = 45
        elif transaction_count < 30:
            score = 75
        else:
            score = 100

        stability_score = float(stability) * 30
        return max(0, min(100, score + stability_score))

    @staticmethod
    def _score_account_age(months):
        if months <= 1:
            return 25
        if months <= 3:
            return 40
        if months <= 6:
            return 60
        if months <= 12:
            return 80
        return 95
