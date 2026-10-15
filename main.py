import os
from datetime import datetime
from dotenv import load_dotenv

from data.data_fetcher import get_multi_tf_data
from signals.signal_generator import generate_signal
from analysis.options_helper import suggest_option
from analysis.kill_zone import apply_kill_zone_filter
from paper_logger import log_trade
from bot import create_bot_application, format_signal_message
from nifty50_stocks import get_nifty50_stocks
from swing_signal import generate_swing_signal

load_dotenv()


async def analyze_instrument(instrument: str):
    print(f"Analyzing {instrument} (Multi-Timeframe)...")

    mtf_data = get_multi_tf_data(instrument)

    df_15m = mtf_data.get("15m")
    df_1h = mtf_data.get("1h")

    if df_15m is None or df_15m.empty:
        return {
            "instrument": instrument,
            "decision": "DO NOT ENTER",
            "reason": ["Failed to fetch 15m data"],
            "bias": "unknown",
            "htf_bias": "unknown"
        }, None, None, None

    signal = generate_signal(df_15m, instrument=instrument, df_1h=df_1h)
    signal = apply_kill_zone_filter(signal)

    option_suggestion = None

    if signal["decision"] == "ENTER" and signal.get("entry"):
        option_suggestion = suggest_option(
            direction=signal["direction"],
            spot_price=signal["entry"],
            instrument=instrument
        )

    log_trade(signal, None, None)
    return signal, option_suggestion, None, None


async def run_analysis(update=None):
    """For Nifty + Bank Nifty (Intraday)"""
    results = []
    for instrument in ["Nifty", "BankNifty"]:
        try:
            signal, option_suggestion, position, pnl = await analyze_instrument(instrument)
            message = format_signal_message(signal, option_suggestion, position, pnl)
            results.append(message)
        except Exception as e:
            results.append(f"Error analyzing {instrument}: {str(e)}")

    full_message = "\n\n".join(results)

    if update:
        await update.message.reply_text(full_message, parse_mode="Markdown")
    else:
        print(full_message)


async def run_stock_scan(update=None):
    """For Nifty 50 Stocks (Swing Trading) - runs every 1 hour"""
    print("Starting Nifty 50 Stocks Swing Scan...")
    
    stocks = get_nifty50_stocks()
    enter_signals = []

    for symbol in stocks:
        try:
            signal = generate_swing_signal(symbol)
            
            if signal["decision"] == "ENTER":
                msg = f"🟢 *SWING ENTER* – {signal['symbol']}\n\n"
                msg += f"*Direction:* {signal.get('direction')}\n"
                msg += f"*Current Price:* ₹{signal.get('current_price')}\n"
                msg += f"*Entry:* `{signal.get('entry')}`\n"
                msg += f"*SL:* `{signal.get('stop_loss')}`\n"
                msg += f"*Target:* `{signal.get('target_1')}`\n\n"
                msg += "*Reasons:*\n"
                for r in signal.get("reason", []):
                    msg += f"• {r}\n"
                
                enter_signals.append(msg)
                
        except Exception as e:
            print(f"Error on {symbol}: {e}")

    if enter_signals:
        full_message = "*Nifty 50 Swing Signals*\n\n" + "\n\n".join(enter_signals)
    else:
        full_message = "No strong Swing signals found in Nifty 50 stocks right now."

    if update:
        await update.message.reply_text(full_message, parse_mode="Markdown")
    else:
        # For auto scan - send to Telegram
        from bot import CHAT_ID
        from telegram import Bot
        import os
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        await bot.send_message(chat_id=CHAT_ID, text=full_message, parse_mode="Markdown")


def main():
    print("Starting SMC Signal Engine Bot (Indices + Nifty 50 Stocks)...")
    app = create_bot_application()
    app.run_polling()


if __name__ == "__main__":
    main()
