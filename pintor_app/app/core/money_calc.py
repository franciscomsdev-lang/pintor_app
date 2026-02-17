# core/money_calc.py
from decimal import Decimal, ROUND_HALF_UP


def subtotal_cents(price_cents: int, qty: Decimal) -> int:
    # price_cents * qty => Decimal de cents
    raw = (Decimal(price_cents) * qty)
    rounded = raw.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(rounded)

# app/domain/money.py  (adição segura)

def mul_decimal(self, qty: Decimal) -> "Money":
    raw = Decimal(self.cents) * qty
    rounded = raw.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return Money(int(rounded))
