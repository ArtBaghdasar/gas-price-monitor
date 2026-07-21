from __future__ import annotations

import asyncio
import logging
import os
from datetime import time
from decimal import Decimal
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from config.settings import PARAMS
from core.report import build_report
from core.runner import run_all
from storage import Database

LOGGER = logging.getLogger(__name__)
TZ = ZoneInfo(os.getenv("BOT_TIMEZONE", "Europe/Moscow"))


def keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔄 Проверить цены", callback_data="prices")],
            [
                InlineKeyboardButton("⚙️ Параметры", callback_data="settings"),
                InlineKeyboardButton("🔕 Отключить отчёт", callback_data="unsubscribe"),
            ],
        ]
    )


def settings_text() -> str:
    return (
        "<b>Параметры расчёта</b>\n\n"
        f"📍 {PARAMS.locality}, {PARAMS.distance_from_mkad_km} км от МКАД\n"
        f"🛢 Газгольдер: {PARAMS.tank_capacity_liters:,} л\n"
        f"⛽ Остаток: {PARAMS.remaining_percent}%\n"
        f"🎯 Уровень после заправки: {PARAMS.target_percent}%\n"
        f"🚚 Объём доставки: {PARAMS.refill_liters:,} л"
    ).replace(",", " ")


async def collect_and_format(db: Database) -> str:
    previous = db.previous_prices()
    results = await asyncio.to_thread(run_all, PARAMS)
    db.save_results(results)
    return build_report(results, previous_prices=previous)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None:
        return
    db: Database = context.application.bot_data["db"]
    db.subscribe(update.effective_chat.id)
    text = (
        "<b>Мониторинг стоимости газа включён</b>\n\n"
        "Бот проверяет цены поставщиков для заданных параметров и присылает "
        "один ежедневный отчёт. Заказы и заявки он не отправляет.\n\n"
        "Нажмите кнопку ниже, чтобы выполнить проверку сейчас."
    )
    await update.effective_message.reply_text(
        text, parse_mode=ParseMode.HTML, reply_markup=keyboard()
    )


async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return
    waiting = await message.reply_text("Проверяю открытые цены поставщиков…")
    db: Database = context.application.bot_data["db"]
    report = await collect_and_format(db)
    await waiting.edit_text(report, reply_markup=keyboard())


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message:
        await update.effective_message.reply_text(
            settings_text(), parse_mode=ParseMode.HTML, reply_markup=keyboard()
        )


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None or update.effective_message is None:
        return
    db: Database = context.application.bot_data["db"]
    db.unsubscribe(update.effective_chat.id)
    await update.effective_message.reply_text(
        "Ежедневная рассылка отключена. Команда /start включит её снова."
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return
    await query.answer()
    if query.data == "prices":
        await query.edit_message_text("Проверяю открытые цены поставщиков…")
        db: Database = context.application.bot_data["db"]
        report = await collect_and_format(db)
        await query.edit_message_text(report, reply_markup=keyboard())
    elif query.data == "settings":
        await query.edit_message_text(
            settings_text(), parse_mode=ParseMode.HTML, reply_markup=keyboard()
        )
    elif query.data == "unsubscribe":
        db: Database = context.application.bot_data["db"]
        if query.message:
            db.unsubscribe(query.message.chat.id)
        await query.edit_message_text(
            "Ежедневная рассылка отключена. Команда /start включит её снова."
        )


async def daily_report(context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.application.bot_data["db"]
    report = await collect_and_format(db)
    for chat_id in db.subscribers():
        try:
            await context.bot.send_message(chat_id=chat_id, text=report, reply_markup=keyboard())
        except Exception:
            LOGGER.exception("Не удалось отправить отчёт в чат %s", chat_id)


def parse_report_time(raw: str) -> time:
    try:
        hour, minute = (int(part) for part in raw.split(":", maxsplit=1))
        return time(hour=hour, minute=minute, tzinfo=TZ)
    except (ValueError, TypeError):
        raise ValueError("REPORT_TIME должен иметь формат HH:MM, например 09:00")


def create_application(token: str, db_path: str | None = None) -> Application:
    application = ApplicationBuilder().token(token).build()
    resolved_db_path = db_path or os.getenv("DATABASE_PATH", "data/gas_monitor.db")
    application.bot_data["db"] = Database(resolved_db_path)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("prices", prices))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("stop", unsubscribe))
    application.add_handler(CallbackQueryHandler(button))

    report_time = parse_report_time(os.getenv("REPORT_TIME", "09:00"))
    if application.job_queue is None:
        raise RuntimeError('Установите пакет с опцией: python-telegram-bot[job-queue]')
    application.job_queue.run_daily(daily_report, time=report_time, name="daily-gas-report")
    return application


def run() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN")
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    create_application(token).run_polling(allowed_updates=Update.ALL_TYPES)
