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
        "Commands:\n"
        "/status – Check bot status"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running ✅")

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
    msg += f"*Target 1:* `{signal.get('target_1')}` (1:2)\n"
    msg += f"*Target 2:* `{signal.get('target_2')}` (1:3)\n\n"

    if position:
        msg += f"*Quantity:* {position.get('quantity', 'N/A')}\n"
        msg += f"*Risk Amount:* ₹{position.get('actual_risk', 'N/A')}\n"

    if pnl:
        msg += f"*Potential Profit (T1):* ₹{pnl.get('potential_profit_t1', 'N/A')}\n"
        msg += f"*Potential Profit (T2):* ₹{pnl.get('potential_profit_t2', 'N/A')}\n\n"

    if option_suggestion and "recommended" in option_suggestion:
        msg += f"*Suggested Option:* `{option_suggestion['recommended']}` (ATM)\n"
        msg += f"*Est. Premium:* ₹{option_suggestion.get('estimated_premium', 'N/A')}\n\n"

    msg += "*Reasons:*\n"
    for r in signal.get("reason", []):
        msg += f"• {r}\n"

    msg += f"\n*Current Zone:* {str(signal.get('current_zone', '')).capitalize()}"
    
    return msg


async def send_signal_to_telegram(application, signal: dict, option_suggestion=None, position=None, pnl=None):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram token or chat ID missing")
        return

    message = format_signal_message(signal, option_suggestion, position, pnl)
    
    try:
        await application.bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")


def create_bot_application():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    return app
