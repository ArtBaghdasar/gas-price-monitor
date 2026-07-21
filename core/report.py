from __future__ import annotations

from datetime import date
from decimal import Decimal

from providers.base import PriceResult


def money(value: Decimal | None, suffix: str = "") -> str:
    if value is None:
        return "—"
    formatted = f"{value:,.2f}".replace(",", " ").replace(".", ",")
    return f"{formatted}{suffix}"


def change_text(current: Decimal, previous: Decimal | None) -> str:
    if previous is None:
        return "🆕 первая проверка"
    delta = current - previous
    if delta == 0:
        return "➖ без изменений"
    arrow = "⬆" if delta > 0 else "⬇"
    sign = "+" if delta > 0 else "−"
    return f"{arrow} {sign}{money(abs(delta))}"


def build_report(
    results: list[PriceResult],
    report_date: date | None = None,
    previous_prices: dict[str, Decimal] | None = None,
) -> str:
    report_date = report_date or date.today()
    previous_prices = previous_prices or {}
    available = sorted(
        (r for r in results if r.status == "ok" and r.price_per_liter is not None),
        key=lambda r: r.price_per_liter,
    )
    unavailable = [r for r in results if r.status != "ok"]

    lines = [f"Стоимость газа на {report_date:%d.%m.%Y}", ""]
    for index, result in enumerate(available, start=1):
        assert result.price_per_liter is not None
        lines.extend(
            [
                f"{index}. {result.supplier}",
                f"   {money(result.price_per_liter, ' ₽/л')}   "
                f"{change_text(result.price_per_liter, previous_prices.get(result.supplier))}",
                f"   {money(result.total_price, ' ₽ за 4 150 л')}",
                "",
            ]
        )

    if unavailable:
        for result in unavailable:
            lines.extend([f"⚠️ {result.supplier}", "   Цена недоступна", ""])

    if available:
        best = available[0]
        lines.extend(
            [
                "Самая низкая цена сегодня:",
                f"{best.supplier} — {money(best.price_per_liter, ' ₽/л')}",
            ]
        )
    else:
        lines.append("Не удалось получить ни одной цены.")

    return "\n".join(lines).strip()
