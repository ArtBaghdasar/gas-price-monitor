from __future__ import annotations

from .ck_gaz import CKGazProvider
from .public_page import PublicPageConfig, PublicPageProvider


def build_providers():
    """Все поставщики, которых бот проверяет при каждом запуске."""
    return [
        CKGazProvider(),
        PublicPageProvider(PublicPageConfig(
            name="ВСК Газ",
            url="https://vsk-gaz.ru/zapravka-gazgoldera",
            preferred_patterns=(r"(?:от\s*)?(\d{1,3}(?:[.,]\d{1,2})?)\s*(?:₽|руб\.?)\s*(?:/|за\s*)?(?:литр|л)",),
        )),
        PublicPageProvider(PublicPageConfig(
            name="СибГаз",
            url="https://sib-gas.ru/product/tekhnicheskie-gazy/zapravka-gazgoldera/filter/clear/apply/",
            minimum_volume_liters=0,
            preferred_patterns=(r"заправка\s+газгольдера.*?от\s*(\d{1,3}(?:[.,]\d{1,2})?)\s*руб(?:\.|лей)?\s*/\s*литр",),
            note="Публичная цена «от»; доставка зависит от расстояния и объёма",
        )),
        PublicPageProvider(PublicPageConfig(
            name="ЗаправкаГаз",
            url="https://zapravkagaz.ru/#calculator",
            page_url="https://zapravkagaz.ru/",
            minimum_volume_liters=4000,
            # Для нашего объёма 4150 л выбираем тариф 4000–8000 л.
            preferred_patterns=(r"от\s*4000\s*л\s*до\s*8000\s*л.*?(\d{1,3}(?:[.,]\d{1,2})?)",),
            note="Тариф для объёма 4 000–8 000 л",
        )),
        PublicPageProvider(PublicPageConfig(
            name="iGAS",
            url="https://igas.su/",
            page_url="https://igas.su/volumes/zapravka-gazgoldera-5000-litrov/",
            preferred_patterns=(r"(?:от\s*)?(\d{1,3}(?:[.,]\d{1,2})?)\s*руб(?:\.|лей)?\s*(?:/|за\s*)?(?:литр|л)",),
            note="Публичная цена для страницы газгольдера 5 000 л",
        )),
        PublicPageProvider(PublicPageConfig(
            name="Блик Газ",
            url="https://blik-gas.ru/",
            page_url="https://blik-gas.ru/volumes/5000/",
            preferred_patterns=(r"от\s*(\d{1,3}(?:[.,]\d{1,2})?)\s*руб(?:\.|лей)?\s*за\s*литр",),
            note="Публичная цена для газгольдера 5 000 л",
        )),
        PublicPageProvider(PublicPageConfig(
            name="МосРегионГаз",
            url="https://mosreggaz.ru/",
            preferred_patterns=(r"цена\s+за\s+литр\s+газа\s+от\s*(\d{1,3}(?:[.,]\d{1,2})?)\s*руб",),
            note="Публичная цена «от» с доставкой по Московской области",
        )),
        PublicPageProvider(PublicPageConfig(
            name="BestГаз",
            url="https://zaprawkagazgoldera.ru/",
        )),
        PublicPageProvider(PublicPageConfig(
            name="GasLPG",
            url="https://gas-lpg.ru/",
        )),
        PublicPageProvider(PublicPageConfig(
            name="Доставим Газ",
            url="https://dostavimgaz.ru/",
        )),
        PublicPageProvider(PublicPageConfig(
            name="VERVEX",
            url="https://msk.vervex.ru/l/nao/kommunarka/",
        )),
        PublicPageProvider(PublicPageConfig(
            name="Быстрый Газ",
            url="https://bistrogaz.ru/",
        )),
    ]
