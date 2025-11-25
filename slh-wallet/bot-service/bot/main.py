from __future__ import annotations

import logging
from typing import Final

import httpx
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from .config import TELEGRAM_BOT_TOKEN, API_BASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("slh_wallet.bot")

API_TIMEOUT: Final = 10.0


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    מסך פתיחה ראשי לבוט הארנק.
    """
    user = update.effective_user
    if not user:
        return

    text = (
        f"שלום @{user.username or user.id}! 🌐\n\n"
        "ברוך הבא ל-SLH Community Wallet 🚀\n\n"
        "הארנק הקהילתי של SLH מאפשר לך:\n"
        "• לרשום כתובת BNB/SLH למערכת\n"
        "• לראות יתרות חיות מרשת BNB\n"
        "• להתחבר למערכת האקו-סיסטם של SLH\n\n"
        "פקודות עיקריות:\n"
        "/wallet – רישום/עדכון ארנק\n"
        "/set_wallet – שמירת כתובות הארנק\n"
        "/balances – צפייה ביתרות בזמן אמת\n"
        "/help – סיכום כל האפשרויות\n\n"
        "המערכת אינה דורשת סיסמה – רק טלגרם + כתובות ארנק."
    )
    await update.effective_chat.send_message(text)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    פקודת עזרה – מציגה את כל הפקודות המרכזיות.
    """
    text = (
        "📘 *עזרה – SLH Community Wallet*\n\n"
        "הפקודות הזמינות בבוט:\n\n"
        "• `/start` – מסך פתיחה והסבר כללי\n"
        "• `/wallet` – הסבר איך לרשום/לעדכן את הארנק שלך\n"
        "• `/set_wallet <כתובת_BNB> [כתובת_SLH]` – שמירת כתובות הארנק במערכת\n"
        "   - אם לא תשלח כתובת SLH, נשתמש באותה כתובת כמו BNB\n"
        "• `/balances` – צפייה ביתרות חיות (BNB + SLH פנימי)\n\n"
        "המערכת מחוברת לשרת ה-SLH ואל רשת BNB Smart Chain.\n"
        "בעתיד יתווספו חיבור למנוע TON Trading Bot Pro ויכולות ניתוח מתקדמות."
    )
    await update.effective_chat.send_message(text, parse_mode="Markdown")


async def cmd_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    הסבר על רישום / עדכון ארנק.
    """
    user = update.effective_user
    if not user:
        return

    text = (
        "📲 *רישום / עדכון ארנק SLH*\n\n"
        "כדי לרשום ארנק, שלח פקודה בפורמט הבא:\n"
        "`/set_wallet <כתובת_BNB> [כתובת_SLH (אופציונלי)]`\n\n"
        "אם לא תשלח כתובת SLH, המערכת תשתמש באותה כתובת כמו BNB.\n\n"
        "דוגמה:\n"
        "`/set_wallet 0xd0617b54fb4b6b66307846f217b4d685800e3da4`\n"
        "או:\n"
        "`/set_wallet 0xd0617b54fb4b6b66307846f217b4d685800e3da4 0xABCDEF...1234`"
    )
    await update.effective_chat.send_message(text, parse_mode="Markdown")


async def cmd_set_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    רישום בפועל של כתובות הארנק ב-API.
    """
    user = update.effective_user
    if not user:
        return

    if len(context.args) < 1:
        await update.effective_chat.send_message(
            "שימוש: /set_wallet <כתובת_BNB> [כתובת_SLH (אופציונלי)]"
        )
        return

    bnb_address = context.args[0].strip()
    slh_address = context.args[1].strip() if len(context.args) > 1 else bnb_address

    payload = {
        "telegram_id": str(user.id),
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "bnb_address": bnb_address,
        "slh_address": slh_address,
    }

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            resp = await client.post(f"{API_BASE_URL}/api/wallet/register", json=payload)
            if resp.status_code != 200:
                logger.error("Register wallet failed: %s %s", resp.status_code, resp.text)
                await update.effective_chat.send_message(
                    "❌ לא הצלחתי לעדכן את הארנק. נסה שוב מאוחר יותר."
                )
                return
    except Exception as e:  # noqa: BLE001
        logger.error("Error talking to API: %s", e)
        await update.effective_chat.send_message(
            "❌ בעיית תקשורת עם השרת. נסה שוב מאוחר יותר."
        )
        return

    await update.effective_chat.send_message(
        "✅ הארנק שלך נרשם/עודכן בהצלחה במערכת SLH."
    )


async def cmd_balances(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    שליפת יתרות הארנק מה-API והצגתן למשתמש.
    """
    user = update.effective_user
    if not user:
        return

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            resp = await client.get(f"{API_BASE_URL}/api/wallet/{user.id}/balances")
            if resp.status_code == 404:
                await update.effective_chat.send_message(
                    "לא נמצא ארנק. השתמש ב-/wallet ולאחר מכן ב-/set_wallet כדי לרשום ארנק."
                )
                return
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:  # noqa: BLE001
        logger.error("Error fetching balances: %s", e)
        await update.effective_chat.send_message(
            "❌ בעיית תקשורת עם השרת. נסה שוב מאוחר יותר."
        )
        return

    text = (
        "🏦 *יתרות SLH ו-BNB*\n\n"
        f"💎 BNB (on-chain): `{data.get('bnb_balance', 0):.6f}`\n"
        f"🪙 SLH on-chain: `{data.get('slh_balance_chain', 0):.6f}`\n"
        f"🧾 SLH פנימי: `{data.get('slh_balance_internal', 0):.6f}`\n\n"
        f"📍 BNB: `{data.get('bnb_address')}`\n"
        f"📍 SLH: `{data.get('slh_address')}`"
    )
    await update.effective_chat.send_message(text, parse_mode="Markdown")


def main() -> None:
    """
    נקודת הכניסה הראשית – הפעלת הבוט במצב polling.
    """
    app: Application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("wallet", cmd_wallet))
    app.add_handler(CommandHandler("set_wallet", cmd_set_wallet))
    app.add_handler(CommandHandler("balances", cmd_balances))

    logger.info("Starting SLH Wallet bot (polling)...")
    app.run_polling()


if __name__ == "__main__":
    main()
