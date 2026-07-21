from decimal import Decimal

from providers import MonitorParams

PARAMS = MonitorParams(
    locality="Коммунарка",
    distance_from_mkad_km=13,
    tank_capacity_liters=5000,
    remaining_percent=Decimal("2"),
    target_percent=Decimal("85"),
    refill_liters=4150,
)
