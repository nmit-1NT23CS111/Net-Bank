from decimal import Decimal

from django.test import TestCase

from accounts.models import Account, CustomUser


class AccountWithdrawalTests(TestCase):
    def test_account_cannot_withdraw_more_than_balance(self):
        user = CustomUser.objects.create_user(username="demo", email="demo@example.com", password="unit-test-only")
        account = Account.objects.create(
            user=user,
            account_number="1234567890",
            balance=Decimal("100.0000"),
            currency="INR",
        )

        self.assertFalse(account.can_withdraw(Decimal("101.0000")))
        self.assertTrue(account.can_withdraw(Decimal("100.0000")))
