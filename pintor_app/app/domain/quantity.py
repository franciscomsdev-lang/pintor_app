# app/domain/quantity.py
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

SCALE_M2 = Decimal("0.001")
SCALE_INT = Decimal("1")

@dataclass(frozen=True, slots=True)
class Quantity:
    value: Decimal

    @staticmethod
    def from_decimal(value: Decimal, unit: str) -> "Quantity":
        if value < 0:
            raise ValueError("Quantity cannot be negative")

        scale = SCALE_M2 if unit == "M2" else SCALE_INT
        q = value.quantize(scale, rounding=ROUND_HALF_UP)
        return Quantity(q)

    @staticmethod
    def from_thousandths(qty_thousandths: int, unit: str = "M2") -> "Quantity":
        # unit default M2 porque thousandths está definido para escala 0.001
        if qty_thousandths < 0:
            raise ValueError("Quantity cannot be negative")
        dec = (Decimal(int(qty_thousandths)) / Decimal(1000))
        return Quantity.from_decimal(dec, unit=unit)

    def to_thousandths(self) -> int:
        scaled = (self.value * Decimal(1000)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return int(scaled)
