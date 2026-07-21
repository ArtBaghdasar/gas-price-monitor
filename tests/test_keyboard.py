from datetime import datetime, timezone
from decimal import Decimal

from bot.app import keyboard
from providers.base import PriceResult


def test_keyboard_contains_provider_url_buttons():
    results = [
        PriceResult(
            supplier="Тест Газ",
            url="https://example.com/price",
            status="ok",
            checked_at=datetime.now(timezone.utc),
            price_per_liter=Decimal("31.50"),
            total_price=Decimal("130725"),
        ),
        PriceResult.unavailable(
            supplier="Нет цены",
            url="https://example.org/calculator",
            note="Цена не найдена",
        ),
    ]

    markup = keyboard(results)
    buttons = [row[0] for row in markup.inline_keyboard[:2]]

    assert buttons[0].url == "https://example.com/price"
    assert "31,50 ₽/л" in buttons[0].text
    assert buttons[1].url == "https://example.org/calculator"
