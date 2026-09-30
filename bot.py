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

# Major Indian market holidays (you can add more later)
MARKET_HOLIDAYS = [
    "2026-01-26",  # Republic Day
    "2026-03-03",  # Holi
    "2026-03-26",  # Ram Navami
    "2026-04-03",  # Good Friday
    "2026-04-14",  # Ambedkar Jayanti
    "2026-05-01",  # Maharashtra Day
    "2026-08-15",  # Independence Day
    "2026-08-27",  # Ganesh Chaturthi
    "2026-10-02",  # Gandhi Jayanti
    "2026-10-20",  # Dussehra
    "2026-11-08",  # Diwali
    "2026-11-09",  # Diwali
    "2026-12-25",  # Christmas
]

def is_market_open() -> bool:
    now = datetime.now(IST)
    
    # Weekend check
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Holiday check
    today_str = now.strftime("%Y-%m-%d")
    if today_str in MARKET_HOLIDAYS:
        return False
    
    # Time check (9:15 AM to 3:30 PM)
    current_time = now.time()
    market_open = time(9, 15)
    market_close = time(15, 30)
    
    return market_open <= current_time <= market_close


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "SMC Signal Engine is active.\n\n"
        "Available commands:\n"
        "/status - Check bot status\n"
        "/scan - Analyze Nifty & Bank Nifty now\n"
        "/summary - Paper trading summary"
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

async def auto_scan(context: ContextTypes.DEFAULT_TYPE):
    if not is_market_open():
        return  # Silently skip if market is closed

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

    # Auto scan every 15 minutes (900 seconds)
    if app.job_queue:
        app.job_queue.run_repeating(auto_scan, interval=900, first=30)

    return app
