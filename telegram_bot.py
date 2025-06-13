import asyncio
import json
from functools import wraps

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_TOKEN, TELEGRAM_USER_ID
from logger import summary
from settings_manager import Settings

def user_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != TELEGRAM_USER_ID:
            await update.message.reply_text("Accès refusé.")
            return
        return await func(update, context)
    return wrapper


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Deriv prêt. Tape /help pour la liste des commandes.")


@user_only
async def set_demo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings: Settings = context.bot_data['settings']
    settings._data['account_mode'] = 'demo'
    settings.save()
    await update.message.reply_text("Mode compte: DEMO ✅")


@user_only
async def set_real(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings: Settings = context.bot_data['settings']
    settings._data['account_mode'] = 'real'
    settings.save()
    await update.message.reply_text("Mode compte: RÉEL ✅")


@user_only
async def set_timeframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings: Settings = context.bot_data['settings']
    if not context.args:
        await update.message.reply_text("Usage: /set_timeframe 1m|5m")
        return
    tf = context.args[0]
    if tf not in ['1m', '5m']:
        await update.message.reply_text("Valeur invalide. Choisir 1m ou 5m.")
        return
    settings._data['timeframe'] = tf
    settings.save()
    await update.message.reply_text(f"Timeframe mis à {tf} ✅")


@user_only
async def set_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings: Settings = context.bot_data['settings']
    if not context.args:
        await update.message.reply_text("Usage: /set_amount <montant>")
        return
    try:
        amt = float(context.args[0])
    except ValueError:
        await update.message.reply_text("Montant invalide.")
        return
    settings._data['trade_amount'] = amt
    settings.save()
    await update.message.reply_text(f"Montant par trade: {amt} ✅")


@user_only
async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings: Settings = context.bot_data['settings']
    if not context.args:
        await update.message.reply_text("Usage: /set_mode auto|manual")
        return
    mode = context.args[0]
    if mode not in ['auto', 'manual']:
        await update.message.reply_text("Mode invalide.")
        return
    settings._data['mode'] = mode
    settings.save()
    await update.message.reply_text(f"Mode : {mode.upper()} ✅")


@user_only
async def journal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wins, losses, rows = summary()
    msg = f"📊 Journal 20 derniers trades\nGagnés: {wins} | Perdus: {losses}\n\n"
    for r in rows[-10:]:
        msg += f"{r['timestamp']} {r['asset']} {r['pattern']} {r['direction']} -> {r['result']}\n"
    await update.message.reply_text(msg)


async def run_telegram(settings, notify_cb):
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Store settings and notify callback
    application.bot_data['settings'] = settings
    application.bot_data['notify_cb'] = notify_cb

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_demo", set_demo))
    application.add_handler(CommandHandler("set_real", set_real))
    application.add_handler(CommandHandler("set_timeframe", set_timeframe))
    application.add_handler(CommandHandler("set_amount", set_amount))
    application.add_handler(CommandHandler("set_mode", set_mode))
    application.add_handler(CommandHandler("journal", journal))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()
