import os
from datetime import datetime, time
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
IST = pytz.timezone("Asia/Kolkata")

MARKET_HOLIDAYS = [
    "2026-01-26", "2026-03-03", "2026-03-26", "2026-04-03",
    "2026-04-14", "2026-05-01", "2026-08-15", "2026-08-27",
    "2026-10-02", "2026-10-20", "2026-11-08", "2026-11-09", "2026-12-25"
]

def is_market_open() -> bool:
    now = datetime.now(IST)
    if now.weekday() >= 5:
        return False
    today_str = now.strftime("%Y-%m-%d")
    if today_str in MARKET_HOLIDAYS:
        return False
    current_time = now.time()
    return time(9, 15) <= current_time <= time(15, 30)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "SMC Signal Engine is active.\n\n"
        "Available commands:\n"
        "/status - Check bot status\n"
        "/scan - Analyze Nifty & Bank Nifty now\n"
        "/summary - Paper trading summary\n"
        "/take 1 or /take 2 - Record your trade"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    market_status = "OPEN ✅" if is_market_open() else "CLOSED ❌"
    await update.message.reply_text(
        f"Bot is running ✅\n"
        f"Market Status: {market_status}\n"
        f"Auto-scan: Every 15 minutes (only during market hours)"
    )

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_market_open():
        await update.message.reply_text(
            "Market is currently closed.\n"
            "Scanning is only allowed between 9:15 AM – 3:30 PM IST on trading days."
        )
        return

    await update.message.reply_text("Analyzing market... Please wait.")
    from main import run_analysis
    await run_analysis(update)

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from paper_logger import get_summary
    summary_text = get_summary()
    await update.message.reply_text(summary_text)

async def take(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User replies /take 1 or /take 2 to record the trade"""
    try:
        lots = int(context.args[0]) if context.args else 1
        if lots not in [1, 2]:
            await update.message.reply_text("Please use /take 1 or /take 2")
            return

        from paper_logger import record_taken_trade
        result = record_taken_trade(lots)
        await update.message.reply_text(result)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}\nUse /take 1 or /take 2")

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

    msg += f"*Index Entry:* `{signal.get('entry')}`\n"
    msg += f"*Index SL:* `{signal.get('stop_loss')}`\n"
    msg += f"*Index Target 1:* `{signal.get('target_1')}`\n"
    msg += f"*Index Target 2:* `{signal.get('target_2')}`\n\n"

    if option_suggestion and "recommended" in option_suggestion:
        msg += f"*Recommended Option:* `{option_suggestion['recommended']}`\n"
        msg += f"*Strike Type:* ATM\n"
        msg += f"*Estimated Premium:* ₹{option_suggestion.get('estimated_premium', 'N/A')}\n\n"

    if position:
        msg += f"*Suggested Lots (1% risk):* {position.get('quantity', 'N/A') // 15 if signal['instrument'] == 'BankNifty' else position.get('quantity', 'N/A') // 25}\n"
        msg += f"*Risk Amount:* ₹{position.get('actual_risk', 'N/A')}\n\n"

    msg += "*Reasons:*\n"
    for r in signal.get("reason", []):
        msg += f"• {r}\n"

    msg += "\n👉 Reply with `/take 1` or `/take 2` if you take this trade."

    return msg

async def auto_scan(context: ContextTypes.DEFAULT_TYPE):
    if not is_market_open():
        return

    from main import run_analysis

    class FakeUpdate:
        class Message:
            async def reply_text(self, text, parse_mode=None):
                await context.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=parse_mode)
        message = Message()
    
    fake_update = FakeUpdate()
    await run_analysis(fake_update)

def create_bot_application():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("take", take))

    if app.job_queue:
        app.job_queue.run_repeating(auto_scan, interval=900, first=30)

    return app
