from decimal import Decimal


class LenderMatchingService:
    @staticmethod
    def match(credit_score, requested_amount, requested_tenure, lenders):
        matches = []
        for lender in lenders:
            if not lender.active:
                continue
            if credit_score < lender.minimum_credit_score:
                continue
            if requested_amount < lender.minimum_loan_amount or requested_amount > lender.maximum_loan_amount:
                continue
            if requested_tenure < lender.minimum_tenure_months or requested_tenure > lender.maximum_tenure_months:
                continue
            matches.append(lender)
        return matches
