from decimal import Decimal

from providers.public_page import PublicPageProvider


def test_parses_public_price():
    html = '<h1>Заправка газгольдера</h1><p>Цена за литр газа от 29,5 руб.</p>'
    assert PublicPageProvider.parse_price(html) == Decimal('29.5')


def test_prefers_volume_tier():
    html = '''
    <table>
      <tr><td>от 2000 л до 4000 л</td><td>32.5</td></tr>
      <tr><td>от 4000 л до 8000 л</td><td>32</td></tr>
    </table>
    '''
    pattern = (r"от\s*4000\s*л\s*до\s*8000\s*л.*?(\d{1,3}(?:[.,]\d{1,2})?)",)
    assert PublicPageProvider.parse_price(html, pattern) == Decimal('32')
