from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class MonitorParams:
    locality: str
    distance_from_mkad_km: int
    tank_capacity_liters: int
    remaining_percent: Decimal
    target_percent: Decimal
    refill_liters: int


@dataclass(frozen=True)
class PriceResult:
    supplier: str
    url: str
    status: str
    checked_at: datetime
    price_per_liter: Decimal | None = None
    total_price: Decimal | None = None
    note: str | None = None

    @classmethod
    def unavailable(cls, supplier: str, url: str, note: str) -> "PriceResult":
        return cls(
            supplier=supplier,
            url=url,
            status="unavailable",
            checked_at=datetime.now(timezone.utc),
            note=note,
        )


class Provider(Protocol):
    name: str
    url: str

    def get_price(self, params: MonitorParams) -> PriceResult: ...
