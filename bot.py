import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "SMC Signal Engine is active.\n\n"
        "Available commands:\n"
        "/status - Check bot status\n"
        "/scan - Analyze Nifty & Bank Nifty now"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running ✅")

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Analyzing market... Please wait.")
    # We will call the analysis from main later
    from main import run_analysis
    await run_analysis(update)

def format_signal_message(signal: dict, option_suggestion: dict = None, position: dict = None, pnl: dict = None) -> str:
    if signal["decision"] == "DO NOT ENTER":
        msg = f"🔴 *DO NOT ENTER* – {signal['instrument']}\n\n"
        msg += f"*Bias:* {signal.get('bias')}\n"
        msg += "*Reasons:*\n"
        for r in signal.get("reason", []):
            msg += f"• {r}\n"
        return msg

    msg = f"🟢 *ENTER SIGNAL* – {signal['instrument']}\n\n"
    msg += f"*Direction:* {signal.get('direction')}\n"
    msg += f"*Bias:* {signal.get('bias')}\n\n"
    msg += f"*Entry:* `{signal.get('entry')}`\n"
    msg += f"*Stop Loss:* `{signal.get('stop_loss')}`\n"
    msg += f"*Target 1:* `{signal.get('target_1')}`\n"
    msg += f"*Target 2:* `{signal.get('target_2')}`\n\n"

    if position:
        msg += f"*Quantity:* {position.get('quantity', 'N/A')}\n"
        msg += f"*Risk Amount:* ₹{position.get('actual_risk', 'N/A')}\n"

    if pnl:
        msg += f"*Potential Profit (T1):* ₹{pnl.get('potential_profit_t1', 'N/A')}\n"
        msg += f"*Potential Profit (T2):* ₹{pnl.get('potential_profit_t2', 'N/A')}\n\n"

    if option_suggestion and "recommended" in option_suggestion:
        msg += f"*Suggested Option:* `{option_suggestion['recommended']}`\n\n"

    msg += "*Reasons:*\n"
    for r in signal.get("reason", []):
        msg += f"• {r}\n"

    return msg

def create_bot_application():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("scan", scan))
    return app
