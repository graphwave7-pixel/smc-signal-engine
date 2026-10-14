import os
from datetime import datetime
from dotenv import load_dotenv

from data.data_fetcher import get_multi_tf_data
from signals.signal_generator import generate_signal
from analysis.options_helper import suggest_option
from analysis.kill_zone import apply_kill_zone_filter
from paper_logger import log_trade
from bot import create_bot_application, format_signal_message

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

    # Generate signal
    signal = generate_signal(df_15m, instrument=instrument, df_1h=df_1h)
    signal = apply_kill_zone_filter(signal)

    option_suggestion = None

    if signal["decision"] == "ENTER" and signal.get("entry"):
        option_suggestion = suggest_option(
            direction=signal["direction"],
            spot_price=signal["entry"],
            instrument=instrument
        )

    # Log the trade (without position sizing)
    log_trade(signal, None, None)

    return signal, option_suggestion, None, None


async def run_analysis(update=None):
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


def main():
    print("Starting SMC Signal Engine Bot (Multi-Timeframe + Strict Rules)...")
    app = create_bot_application()
    app.run_polling()


if __name__ == "__main__":
    main()
