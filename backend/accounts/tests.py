from django.test import TestCase

from .models import Account


class AccountNumberGenerationTests(TestCase):
    def test_generated_account_number_is_ten_digits(self):
        account_number = Account.generate_account_number()

        self.assertEqual(len(account_number), 10)
        self.assertTrue(account_number.isdigit())
