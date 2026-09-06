from decimal import Decimal, ROUND_HALF_UP


class EMICalculationService:
    @staticmethod
    def calculate(principal, annual_interest_rate, tenure_months):
        principal = Decimal(str(principal))
        annual_interest_rate = Decimal(str(annual_interest_rate))
        tenure_months = int(tenure_months)

        if principal <= 0:
            raise ValueError("Principal amount must be greater than zero.")
        if tenure_months <= 0:
            raise ValueError("Tenure must be greater than zero.")
        if annual_interest_rate < 0:
            raise ValueError("Annual interest rate cannot be negative.")

        if annual_interest_rate == 0:
            emi = principal / Decimal(tenure_months)
            total_repayment = emi * Decimal(tenure_months)
            total_interest = total_repayment - principal
            return {
                "emi": emi.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                "total_interest": total_interest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                "total_repayment": total_repayment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            }

        monthly_rate = annual_interest_rate / Decimal("1200")
        factor = (Decimal("1") + monthly_rate) ** Decimal(tenure_months)
        emi = (principal * monthly_rate * factor) / (factor - Decimal("1"))
        total_repayment = emi * Decimal(tenure_months)
        total_interest = total_repayment - principal

        return {
            "emi": emi.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "total_interest": total_interest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "total_repayment": total_repayment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        }
