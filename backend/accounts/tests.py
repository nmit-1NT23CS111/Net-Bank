from django.test import TestCase

from .models import Account, CustomUser, OAuthProvider
from .serializers import OAuthCallbackSerializer


class AccountNumberGenerationTests(TestCase):
    def test_generated_account_number_is_ten_digits(self):
        account_number = Account.generate_account_number()

        self.assertEqual(len(account_number), 10)
        self.assertTrue(account_number.isdigit())


class OAuthCallbackSerializerTests(TestCase):
    def test_callback_serializer_accepts_google_payload_without_provider(self):
        payload = {
            "code": "auth-code",
            "state": "oauth-state",
            "frontend_url": "http://localhost:5173",
        }

        serializer = OAuthCallbackSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["code"], "auth-code")


class GoogleOAuthExistingEmailLinkTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="badpanther333",
            email="badpanther333@gmail.com",
            password="TestPassword123!",
            first_name="Bad",
            last_name="Panther",
            email_verified=False,
            is_active=True,
        )

    def test_existing_email_is_linked_to_google_provider(self):
        self.assertEqual(CustomUser.objects.filter(email="badpanther333@gmail.com").count(), 1)
        self.assertFalse(OAuthProvider.objects.filter(provider="google", provider_email="badpanther333@gmail.com").exists())
