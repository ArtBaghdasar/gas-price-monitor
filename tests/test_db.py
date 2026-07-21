from datetime import datetime, timezone
from decimal import Decimal

from providers.base import PriceResult
from storage import Database


def result(price: str) -> PriceResult:
    value = Decimal(price)
    return PriceResult(
        supplier="СК-Газ",
        url="https://example.test",
        status="ok",
        checked_at=datetime.now(timezone.utc),
        price_per_liter=value,
        total_price=value * 4150,
    )


def test_subscribe_and_unsubscribe(tmp_path):
    db = Database(tmp_path / "test.db")
    db.subscribe(123)
    assert db.subscribers() == [123]
    db.unsubscribe(123)
    assert db.subscribers() == []


def test_previous_price(tmp_path):
    db = Database(tmp_path / "test.db")
    db.save_results([result("31.50")])
    db.save_results([result("32.00")])
    assert db.previous_prices()["СК-Газ"] == Decimal("31.50")
