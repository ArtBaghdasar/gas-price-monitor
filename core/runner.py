from __future__ import annotations

from providers import CKGazProvider, MonitorParams, PriceResult


def run_all(params: MonitorParams) -> list[PriceResult]:
    providers = [CKGazProvider()]
    return [provider.get_price(params) for provider in providers]
