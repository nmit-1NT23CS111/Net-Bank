from decimal import Decimal


class OfferRankingService:
    @staticmethod
    def rank(eligible_lenders, credit_score, requested_amount, requested_tenure):
        ranked = []
        if not eligible_lenders:
            return ranked

        min_rate = min(Decimal(str(l.minimum_interest_rate)) for l in eligible_lenders)
        max_rate = max(Decimal(str(l.maximum_interest_rate)) for l in eligible_lenders)

        for lender in eligible_lenders:
            interest_rate = Decimal(str(lender.minimum_interest_rate))
            if max_rate == min_rate:
                rate_score = Decimal("100")
            else:
                spread = max(Decimal("0.01"), max_rate - min_rate)
                rate_score = Decimal("100") - ((interest_rate - min_rate) / spread) * Decimal("100")
            amount_score = Decimal("100") if Decimal(str(requested_amount)) <= lender.maximum_loan_amount else Decimal("60")
            tenure_score = Decimal("100") if requested_tenure <= lender.maximum_tenure_months else Decimal("65")
            risk_score = Decimal(str(max(50, min(100, 100 - (lender.minimum_credit_score - credit_score) * 0.5))))

            offer_score = (
                rate_score * Decimal("0.40")
                + amount_score * Decimal("0.25")
                + tenure_score * Decimal("0.20")
                + risk_score * Decimal("0.15")
            )
            ranked.append({"lender": lender, "offer_score": int(offer_score.quantize(Decimal("1"), rounding="ROUND_HALF_UP"))})

        ranked.sort(key=lambda item: item["offer_score"], reverse=True)
        return ranked
