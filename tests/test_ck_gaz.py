from decimal import Decimal

import pytest

from providers.ck_gaz import CKGazProvider


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        ("<h1>Заправляем газгольдеры от 32,00 ₽/литр</h1>", Decimal("32.00")),
        ("<div>*от 4000л = от 31.5 руб./л.</div>", Decimal("31.5")),
        ("<span>Цена 33 ₽ за литр</span>", Decimal("33")),
    ],
)
def test_parse_price(html: str, expected: Decimal) -> None:
    assert CKGazProvider.parse_price(html) == expected


def test_missing_price() -> None:
    with pytest.raises(ValueError):
        CKGazProvider.parse_price("<html>Цена по запросу</html>")
