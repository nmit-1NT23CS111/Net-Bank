from __future__ import annotations

import statistics
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Q, Sum
from django.utils import timezone

from accounts.models import Account
from transactions.models import Transaction


class CreditFeatureService:
    """Derive explainable financial signals from the user's existing bank activity."""

    @staticmethod
    def get_features(user, window_days=90):
        accounts = Account.objects.filter(user=user, status="active")
        account_ids = list(accounts.values_list("id", flat=True))

        if not account_ids:
            return {
                "monthly_income": Decimal("0.00"),
                "monthly_expenses": Decimal("0.00"),
                "average_balance": Decimal("0.00"),
                "transaction_count": 0,
                "transaction_stability": 0.0,
                "income_stability": 0.0,
                "expense_to_income_ratio": 0.0,
                "account_age_months": 0,
                "balance_volatility": 0.0,
                "existing_debt": Decimal("0.00"),
                "repayment_behavior_score": 100,
            }

        cutoff = timezone.now() - timedelta(days=window_days)
        transactions = (
            Transaction.objects.filter(
                Q(from_account__user=user) | Q(to_account__user=user),
                status="completed",
                created_at__gte=cutoff,
            )
            .select_related("from_account", "to_account")
            .order_by("created_at")
        )

        monthly_income = Decimal("0.00")
        monthly_expenses = Decimal("0.00")
        income_amounts = []
        expense_amounts = []
        completed_transaction_amounts = []

        for txn in transactions:
            amount = txn.amount
            completed_transaction_amounts.append(float(amount))
            if txn.to_account and txn.to_account.user_id == user.id and txn.from_account.user_id != user.id:
                income_amounts.append(float(amount))
                monthly_income += amount
            if txn.from_account.user_id == user.id and txn.to_account is not None and txn.to_account.user_id != user.id:
                expense_amounts.append(float(amount))
                monthly_expenses += amount

        if transactions.exists():
            monthly_income = monthly_income / Decimal(max(1, (window_days / 30)))
            monthly_expenses = monthly_expenses / Decimal(max(1, (window_days / 30)))

        avg_balance = accounts.aggregate(avg=Avg("balance"))["avg"] or Decimal("0.00")
        oldest_account = accounts.order_by("created_at").first()
        account_age_months = 0
        if oldest_account:
            age_days = (timezone.now() - oldest_account.created_at).days
            account_age_months = max(0, age_days // 30)

        transaction_count = transactions.count()
        transaction_stability = 0.0
        income_stability = 0.0
        if len(completed_transaction_amounts) > 1:
            transaction_stability = 1.0 - min(1.0, statistics.pstdev(completed_transaction_amounts) / max(1.0, statistics.mean(completed_transaction_amounts)))
        if len(income_amounts) > 1:
            income_stability = 1.0 - min(1.0, statistics.pstdev(income_amounts) / max(1.0, statistics.mean(income_amounts)))

        expense_to_income_ratio = Decimal("0.00")
        if monthly_income > 0:
            expense_to_income_ratio = monthly_expenses / monthly_income
        elif monthly_expenses > 0:
            expense_to_income_ratio = Decimal("1.00")

        balance_volatility = Decimal("0.00")
        balance_list = list(accounts.values_list("balance", flat=True))
        if len(balance_list) > 1:
            avg_balance_value = float(sum(balance_list) / len(balance_list))
            if avg_balance_value > 0:
                balance_volatility = Decimal(str(abs(float(max(balance_list)) - float(min(balance_list))) / max(avg_balance_value, 1.0)))

        return {
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "average_balance": avg_balance,
            "transaction_count": transaction_count,
            "transaction_stability": max(0.0, min(1.0, transaction_stability)),
            "income_stability": max(0.0, min(1.0, income_stability)),
            "expense_to_income_ratio": expense_to_income_ratio,
            "account_age_months": account_age_months,
            "balance_volatility": balance_volatility,
            "existing_debt": Decimal("0.00"),
            "repayment_behavior_score": 100,
        }
