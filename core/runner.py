from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from providers import MonitorParams, PriceResult, build_providers


def run_all(params: MonitorParams) -> list[PriceResult]:
    """Проверяет всех поставщиков параллельно.

    Ошибка одного сайта не прерывает общий отчёт. Порядок результатов остаётся
    таким же, как в реестре поставщиков.
    """
    providers = build_providers()
    indexed_results: dict[int, PriceResult] = {}

    with ThreadPoolExecutor(max_workers=min(8, len(providers))) as executor:
        futures = {
            executor.submit(provider.get_price, params): (index, provider)
            for index, provider in enumerate(providers)
        }
        for future in as_completed(futures):
            index, provider = futures[future]
            try:
                indexed_results[index] = future.result()
            except Exception as exc:  # защита общего отчёта от сбоя адаптера
                indexed_results[index] = PriceResult.unavailable(
                    provider.name, provider.url, f"Ошибка адаптера: {exc}"
                )

    return [indexed_results[index] for index in range(len(providers))]
