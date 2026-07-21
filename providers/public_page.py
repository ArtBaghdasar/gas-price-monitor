from __future__ import annotations

import html as html_lib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import httpx

from .base import MonitorParams, PriceResult


@dataclass(frozen=True)
class PublicPageConfig:
    name: str
    url: str
    page_url: str | None = None
    minimum_volume_liters: int = 0
    preferred_patterns: tuple[str, ...] = ()
    note: str = "Публичная цена с сайта поставщика"


class PublicPageProvider:
    """Извлекает публичную цену за литр из страницы поставщика.

    Адаптер ничего не отправляет на сайт и не заполняет формы. Для сайтов,
    где точная цена появляется только после интерактивного расчёта, возвращает
    статус unavailable вместо выдуманного значения.
    """

    GENERIC_PATTERNS = (
        r"(?:цена\s+за\s+(?:1\s*)?литр(?:\s+газа)?|стоимость(?:\s+литра)?|цена)(?:\s*[:—-])?\s*(?:от\s*)?(\d{1,3}(?:[.,]\d{1,2})?)\s*(?:₽|руб(?:\.|лей)?)",
        r"(?:от\s*)?(\d{1,3}(?:[.,]\d{1,2})?)\s*(?:₽|руб(?:\.|лей)?)\s*(?:/|за\s*)?(?:1\s*)?(?:литр|л)(?![а-я])",
    )

    def __init__(self, config: PublicPageConfig, timeout_seconds: float = 25.0) -> None:
        self.config = config
        self.name = config.name
        self.url = config.url
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _plain_text(html: str) -> str:
        text = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
        text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html_lib.unescape(text).replace("\xa0", " ")
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _decimal(raw: str) -> Decimal | None:
        try:
            value = Decimal(raw.replace(" ", "").replace(",", "."))
        except InvalidOperation:
            return None
        return value if Decimal("10") <= value <= Decimal("100") else None

    @classmethod
    def parse_price(cls, html: str, preferred_patterns: tuple[str, ...] = ()) -> Decimal:
        text = cls._plain_text(html)
        patterns = preferred_patterns + cls.GENERIC_PATTERNS
        for pattern in patterns:
            for match in re.finditer(pattern, text, flags=re.I):
                value = cls._decimal(match.group(1))
                if value is not None:
                    return value
        raise ValueError("На публичной странице не найдена актуальная цена за литр")

    def get_price(self, params: MonitorParams) -> PriceResult:
        if params.refill_liters < self.config.minimum_volume_liters:
            return PriceResult.unavailable(
                self.name,
                self.url,
                f"Публичная цена действует от {self.config.minimum_volume_liters} л",
            )

        target_url = self.config.page_url or self.config.url
        try:
            with httpx.Client(
                timeout=self.timeout_seconds,
                follow_redirects=True,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "Chrome/124.0 Safari/537.36"
                    ),
                    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.7",
                },
            ) as client:
                response = client.get(target_url)
                response.raise_for_status()

            price = self.parse_price(response.text, self.config.preferred_patterns)
            total = (price * Decimal(params.refill_liters)).quantize(Decimal("0.01"))
            return PriceResult(
                supplier=self.name,
                url=self.url,
                status="ok",
                checked_at=datetime.now(timezone.utc),
                price_per_liter=price,
                total_price=total,
                note=self.config.note,
            )
        except (httpx.HTTPError, ValueError) as exc:
            return PriceResult.unavailable(self.name, self.url, str(exc))
