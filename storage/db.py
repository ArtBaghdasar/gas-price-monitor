from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from providers.base import PriceResult


class Database:
    def __init__(self, path: str | Path = "data/gas_monitor.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS subscribers (
                    chat_id INTEGER PRIMARY KEY,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier TEXT NOT NULL,
                    checked_at TEXT NOT NULL,
                    price_per_liter TEXT,
                    total_price TEXT,
                    status TEXT NOT NULL,
                    note TEXT
                );
                """
            )
            connection.commit()

    def subscribe(self, chat_id: int) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                INSERT INTO subscribers(chat_id, enabled, created_at)
                VALUES (?, 1, ?)
                ON CONFLICT(chat_id) DO UPDATE SET enabled = 1
                """,
                (chat_id, datetime.now(timezone.utc).isoformat()),
            )
            connection.commit()

    def unsubscribe(self, chat_id: int) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                "UPDATE subscribers SET enabled = 0 WHERE chat_id = ?", (chat_id,)
            )
            connection.commit()

    def subscribers(self) -> list[int]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT chat_id FROM subscribers WHERE enabled = 1"
            ).fetchall()
        return [int(row["chat_id"]) for row in rows]

    def save_results(self, results: list[PriceResult]) -> None:
        rows = [
            (
                result.supplier,
                result.checked_at.isoformat(),
                str(result.price_per_liter) if result.price_per_liter is not None else None,
                str(result.total_price) if result.total_price is not None else None,
                result.status,
                result.note,
            )
            for result in results
        ]
        with closing(self._connect()) as connection:
            connection.executemany(
                """
                INSERT INTO prices(
                    supplier, checked_at, price_per_liter, total_price, status, note
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            connection.commit()

    def previous_prices(self) -> dict[str, Decimal]:
        """Последняя цена до самого свежего запуска по каждому поставщику."""
        query = """
            WITH ranked AS (
                SELECT supplier, price_per_liter,
                       ROW_NUMBER() OVER (
                           PARTITION BY supplier ORDER BY checked_at DESC, id DESC
                       ) AS row_number
                FROM prices
                WHERE status = 'ok' AND price_per_liter IS NOT NULL
            )
            SELECT supplier, price_per_liter
            FROM ranked
            WHERE row_number = 2
        """
        with closing(self._connect()) as connection:
            rows = connection.execute(query).fetchall()
        return {row["supplier"]: Decimal(row["price_per_liter"]) for row in rows}
