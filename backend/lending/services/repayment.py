from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from lending.models import Repayment


class RepaymentScheduleService:
    @staticmethod
    def generate(loan):
        schedule = []
        for installment_number in range(1, loan.tenure_months + 1):
            due_date = timezone.now().date() + timedelta(days=30 * installment_number)
            repayment = Repayment.objects.create(
                loan=loan,
                installment_number=installment_number,
                due_date=due_date,
                amount=loan.emi,
                paid_amount=Decimal("0.00"),
                status=Repayment.STATUS_PENDING,
            )
            schedule.append(repayment)
        return schedule


class RepaymentProcessingService:
    @staticmethod
    def process(repayment, payment_amount):
        payment_amount = Decimal(str(payment_amount))
        if payment_amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        repayment.paid_amount += payment_amount
        if repayment.paid_amount >= repayment.amount:
            repayment.status = Repayment.STATUS_PAID
            repayment.paid_at = timezone.now()
        else:
            repayment.status = Repayment.STATUS_PARTIAL
            repayment.paid_at = timezone.now()

        repayment.save(update_fields=["paid_amount", "status", "paid_at"])
        return repayment
