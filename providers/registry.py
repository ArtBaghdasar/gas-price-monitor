from __future__ import annotations

from .ck_gaz import CKGazProvider
from .public_page import PublicPageConfig, PublicPageProvider

REGISTRY_VERSION = "2026-07-21-19-sources"


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
        PublicPageProvider(PublicPageConfig(
            name="GasRegion",
            url="https://gasregion.su/zapravka-gazgolderov-gazom/",
            preferred_patterns=(
                r"(\d{1,3}(?:[.,]\d{1,2})?)\s*руб(?:\.|лей)?\s*за\s*1\s*литр",
                r"цена\s+на\s+газ.*?(\d{1,3}(?:[.,]\d{1,2})?)\s*руб",
            ),
            note="Публичная цена с доставкой по Москве и Московской области",
        )),
        PublicPageProvider(PublicPageConfig(
            name="РосАвтономГаз",
            url="https://www.rosavtonomgaz.ru/gaz-propan-butan/zapravka-gazgoldera/",
            preferred_patterns=(
                r"цена\s+за\s+литр.*?(\d{1,3}(?:[.,]\d{1,2})?)\s*(?:₽|руб)",
                r"(\d{1,3}(?:[.,]\d{1,2})?)\s*(?:₽|руб)\s*(?:/|за)\s*(?:литр|л)",
            ),
            note="Цена из публичной страницы или калькулятора; при отсутствии значения требуется уточнение",
        )),
        PublicPageProvider(PublicPageConfig(
            name="Сириус Ойл",
            url="https://oil-sirius.ru/",
            preferred_patterns=(
                r"цена\s+газа\s+на\s+сегодня\s*(\d{1,3}(?:[.,]\d{1,2})?)",
                r"пропан.*?(\d{1,3}(?:[.,]\d{1,2})?)\s*руб\s*/\s*литр",
            ),
            note="Публичная цена пропана для газгольдера",
        )),
        PublicPageProvider(PublicPageConfig(
            name="Астин-групп",
            url="https://astin-ltd.ru/zapravka-gazgoldera/",
            preferred_patterns=(
                r"по\s+цене\s+от\s*(\d{1,3}(?:[.,]\d{1,2})?)\s*руб(?:лей)?\s+за\s+литр",
            ),
            note="Публичная цена «от» по Московской области",
        )),
        PublicPageProvider(PublicPageConfig(
            name="Отличный газ",
            url="https://finegaz.ru/dostavka-gaza/zapravka-gazgoldera/",
            preferred_patterns=(
                r"цена\s+от\s*(\d{1,3}(?:[.,]\d{1,2})?)\s*руб\.?\s*/\s*литр",
                r"стоимость\s+газа\s+с\s+доставкой\s+от\s*(\d{1,3}(?:[.,]\d{1,2})?)\s*руб",
            ),
            note="Публичная цена «от» с доставкой",
        )),
        PublicPageProvider(PublicPageConfig(
            name="МрГаз",
            url="https://mrgaz.ru/",
            page_url="https://mrgaz.ru/",
            preferred_patterns=(
                r"специальной\s+цене\s*(\d{1,3}(?:[.,]\d{1,2})?)\s*руб\s*литр",
                r"цене\s*(\d{1,3}(?:[.,]\d{1,2})?)\s*руб\s*/?\s*литр",
            ),
            note="Публичная акционная цена; срок акции указан на сайте",
        )),
        PublicPageProvider(PublicPageConfig(
            name="АБАС",
            url="https://msk-toplivo.ru/uslugi/dostavka-gaza-dlia-zapravki-gazgolderov/",
            minimum_volume_liters=2000,
            preferred_patterns=(
                r"минимальный\s+заказ.*?от\s*(\d{1,3}(?:[.,]\d{1,2})?)\s*руб\.?\s*/\s*литр",
                r"от\s*(\d{1,3}(?:[.,]\d{1,2})?)\s*руб\.?\s*/\s*литр",
            ),
            note="Публичная цена «от», минимальный заказ 2 000 л",
        )),
    ]
