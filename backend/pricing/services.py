from decimal import Decimal, ROUND_HALF_UP

from .models import FarePolicy, PricingAdjustment

CENT = Decimal("0.01")


def money(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


class CurrencyService:
    @staticmethod
    def validate(currency):
        if len(currency) != 3 or not currency.isalpha():
            raise ValueError("currency must be a three-letter ISO code.")
        return currency.upper()


class PolicyEngine:
    @staticmethod
    def fare_policy(code):
        if not code:
            return None
        return FarePolicy.objects.filter(code=code, active=True).first()

    @staticmethod
    def adjustments(currency, promo_code=None):
        rules = PricingAdjustment.objects.filter(active=True).filter(currency__in=("", currency)).order_by("priority", "code")
        return [rule for rule in rules if rule.adjustment_type != PricingAdjustment.PROMO or rule.promo_code.upper() == (promo_code or "").upper()]


class FareRulesEngine:
    @staticmethod
    def evaluate(policy):
        if not policy:
            return {"fare_family": None, "fare_basis": None, "refund": {}, "cancellation": {}, "date_change": {}, "baggage": {}, "ancillaries": {}}
        return {
            "fare_family": policy.fare_family,
            "fare_basis": policy.fare_basis,
            "refund": {"refundable": policy.refundable, **policy.refund_rules},
            "cancellation": {"allowed": policy.cancellation_allowed, "penalty": str(money(policy.cancellation_penalty)), "currency": policy.currency},
            "date_change": {"allowed": policy.date_change_allowed, "penalty": str(money(policy.date_change_penalty)), "currency": policy.currency},
            "baggage": policy.baggage_rules,
            "ancillaries": policy.ancillary_rules,
        }


class PricingEngine:
    """Provider-independent price calculator using declarative adjustment policies."""

    @staticmethod
    def _line(code, name, amount, category):
        return {"code": code, "name": name, "amount": str(money(amount)), "category": category}

    @classmethod
    def quote(cls, request):
        currency = CurrencyService.validate(request["currency"])
        passenger_count = sum(item["quantity"] for item in request["passengers"])
        base_fare = money(Decimal(request["base_fare"]) * passenger_count)
        lines = [cls._line("BASE_FARE", "Base fare", base_fare, "base_fare")]
        totals = {"tax": Decimal(0), "markup": Decimal(0), "service_fee": Decimal(0), "discount": Decimal(0), "promo": Decimal(0)}

        for tax in request.get("taxes", []):
            amount = money(Decimal(tax["amount"]) * passenger_count)
            totals["tax"] += amount
            lines.append(cls._line(tax.get("code", "TAX"), tax.get("name", "Tax"), amount, "tax"))

        taxable_base = base_fare + totals["tax"]
        for rule in PolicyEngine.adjustments(currency, request.get("promo_code")):
            amount = money(taxable_base * rule.amount / Decimal(100)) if rule.amount_type == PricingAdjustment.PERCENTAGE else money(rule.amount)
            category = rule.adjustment_type
            totals[category] += amount
            lines.append(cls._line(rule.code, rule.name, -amount if category in ("discount", "promo") else amount, category))

        ancillary_total = sum((Decimal(item["amount"]) * item.get("quantity", 1) for item in request.get("ancillaries", [])), Decimal(0))
        seat_total = sum((Decimal(item["amount"]) * item.get("quantity", 1) for item in request.get("seats", [])), Decimal(0))
        if ancillary_total:
            lines.append(cls._line("ANCILLARIES", "Ancillary services", ancillary_total, "ancillary"))
        if seat_total:
            lines.append(cls._line("SEATS", "Seat selection", seat_total, "seat"))
        grand_total = money(base_fare + totals["tax"] + totals["markup"] + totals["service_fee"] - totals["discount"] - totals["promo"] + ancillary_total + seat_total)
        policy = PolicyEngine.fare_policy(request.get("fare_policy_code"))
        return {
            "currency": currency,
            "passenger_count": passenger_count,
            "breakdown": lines,
            "totals": {"base_fare": str(base_fare), "taxes": str(money(totals["tax"])), "markup": str(money(totals["markup"])), "service_fees": str(money(totals["service_fee"])), "discounts": str(money(totals["discount"] + totals["promo"])), "ancillaries": str(money(ancillary_total)), "seats": str(money(seat_total)), "grand_total": str(grand_total)},
            "fare_rules": FareRulesEngine.evaluate(policy),
        }
