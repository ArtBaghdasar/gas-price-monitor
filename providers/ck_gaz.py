from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import httpx

from .base import MonitorParams, PriceResult


class CKGazProvider:
    """СК-Газ: извлекает опубликованную цену из HTML без отправки заявки."""

    name = "СК-Газ"
    url = "https://zapravka-gazgoldera.ck-gaz.ru/"
    minimum_volume_liters = 4000

    # Поддерживает варианты: 32,00 ₽/литр, 32.00 руб./л, от 32 ₽/л.
    PRICE_PATTERNS = (
        re.compile(r"(?:от\s*)?(\d{1,3}(?:[\s.,]\d{1,2})?)\s*(?:₽|руб\.?)[\s/]*(?:литр|л)", re.I),
        re.compile(r"(?:от\s*)?(\d{1,3}(?:[\s.,]\d{1,2})?)\s*(?:₽|руб\.?)\s*(?:за\s*)?(?:литр|л)", re.I),
    )

    def __init__(self, timeout_seconds: float = 20.0) -> None:
        self.timeout_seconds = timeout_seconds

    @classmethod
    def parse_price(cls, html: str) -> Decimal:
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)

        candidates: list[Decimal] = []
        for pattern in cls.PRICE_PATTERNS:
            for match in pattern.finditer(text):
                raw = match.group(1).replace(" ", "").replace(",", ".")
                try:
                    value = Decimal(raw)
                except InvalidOperation:
                    continue
                if Decimal("10") <= value <= Decimal("100"):
                    candidates.append(value)

        if not candidates:
            raise ValueError("На странице не найдена цена за литр")

        # Первая цена на лендинге обычно является основной рекламируемой ценой.
        return candidates[0]

    def get_price(self, params: MonitorParams) -> PriceResult:
        if params.refill_liters < self.minimum_volume_liters:
            return PriceResult.unavailable(
                self.name,
                self.url,
                f"Опубликованная цена действует от {self.minimum_volume_liters} л",
            )

        try:
            with httpx.Client(
                timeout=self.timeout_seconds,
                follow_redirects=True,
                headers={"User-Agent": "GasPriceMonitor/0.1 (+daily public price check)"},
            ) as client:
                response = client.get(self.url)
                response.raise_for_status()

            price = self.parse_price(response.text)
            total = (price * Decimal(params.refill_liters)).quantize(Decimal("0.01"))
            return PriceResult(
                supplier=self.name,
                url=self.url,
                status="ok",
                checked_at=datetime.now(timezone.utc),
                price_per_liter=price,
                total_price=total,
                note=f"Публичная цена для заказа от {self.minimum_volume_liters} л",
            )
        except (httpx.HTTPError, ValueError) as exc:
            return PriceResult.unavailable(self.name, self.url, str(exc))
