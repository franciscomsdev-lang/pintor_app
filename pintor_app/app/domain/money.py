from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

@dataclass(frozen=True, slots=True)
class Money:
    cents: int
    currency: str = "BRL"

    def __add__(self, other: "Money") -> "Money":
        self._assert_currency(other)
        return Money(self.cents + other.cents, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_currency(other)
        return Money(self.cents - other.cents, self.currency)

    def mul_int(self, n: int) -> "Money":
        return Money(self.cents * int(n), self.currency)

    def _assert_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")

    



    def mul_decimal(self, qty: Decimal) -> "Money":
        raw = Decimal(self.cents) * qty
        rounded = raw.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return Money(int(rounded))

