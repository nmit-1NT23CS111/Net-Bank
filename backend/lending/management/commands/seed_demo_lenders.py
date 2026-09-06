from django.core.management.base import BaseCommand

from lending.models import Lender


class Command(BaseCommand):
    help = "Seed demo lenders for the prototype lending engine"

    def handle(self, *args, **options):
        lenders = [
            {
                "name": "Lender Alpha",
                "minimum_credit_score": 65,
                "maximum_loan_amount": 100000,
                "minimum_loan_amount": 15000,
                "minimum_interest_rate": 12.50,
                "maximum_interest_rate": 18.00,
                "minimum_tenure_months": 12,
                "maximum_tenure_months": 36,
                "active": True,
            },
            {
                "name": "Lender Beta",
                "minimum_credit_score": 70,
                "maximum_loan_amount": 500000,
                "minimum_loan_amount": 25000,
                "minimum_interest_rate": 11.00,
                "maximum_interest_rate": 15.00,
                "minimum_tenure_months": 12,
                "maximum_tenure_months": 60,
                "active": True,
            },
            {
                "name": "Lender Gamma",
                "minimum_credit_score": 60,
                "maximum_loan_amount": 200000,
                "minimum_loan_amount": 10000,
                "minimum_interest_rate": 14.50,
                "maximum_interest_rate": 20.00,
                "minimum_tenure_months": 6,
                "maximum_tenure_months": 48,
                "active": True,
            },
        ]

        created = 0
        for config in lenders:
            obj, was_created = Lender.objects.update_or_create(name=config["name"], defaults=config)
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} demo lenders."))
