import os
from datetime import datetime
from dotenv import load_dotenv

from data.data_fetcher import get_nifty_data, get_banknifty_data, get_multi_tf_data
from signals.signal_generator import generate_signal
from analysis.options_helper import suggest_option
from analysis.kill_zone import apply_kill_zone_filter
from position_sizing import calculate_position_size, calculate_rr_and_pnl
from paper_logger import log_trade
from bot import create_bot_application, format_signal_message

load_dotenv()

CAPITAL = 100000
RISK_PERCENT = 1.0
NIFTY_LOT_SIZE = 25
BANKNIFTY_LOT_SIZE = 15


async def analyze_instrument(instrument: str):
    print(f"Analyzing {instrument} (Multi-Timeframe)...")

    # Fetch multi-timeframe data
    mtf_data = get_multi_tf_data(instrument)

    df_15m = mtf_data.get("15m")
    df_1h = mtf_data.get("1h")

    if df_15m is None or df_15m.empty:
        return {
            "instrument": instrument,
            "decision": "DO NOT ENTER",
            "reason": ["Failed to fetch 15m data"]
        }, None, None, None

    lot_size = NIFTY_LOT_SIZE if instrument.lower() == "nifty" else BANKNIFTY_LOT_SIZE

    # Generate signal with multi-timeframe
    signal = generate_signal(df_15m, instrument=instrument, df_1h=df_1h)
    signal = apply_kill_zone_filter(signal)

    option_suggestion = None
    position = None
    pnl = None

    if signal["decision"] == "ENTER" and signal.get("entry") and signal.get("stop_loss"):
        option_suggestion = suggest_option(
            direction=signal["direction"],
            spot_price=signal["entry"],
            instrument=instrument
        )

        position = calculate_position_size(
            capital=CAPITAL,
            risk_percent=RISK_PERCENT,
            entry=signal["entry"],
            stop_loss=signal["stop_loss"],
            lot_size=lot_size
        )

        pnl = calculate_rr_and_pnl(
            entry=signal["entry"],
            stop_loss=signal["stop_loss"],
            target1=signal.get("target_1"),
            target2=signal.get("target_2"),
            quantity=position["quantity"]
        )

    log_trade(signal, position, pnl)
    return signal, option_suggestion, position, pnl


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
    print("Starting SMC Signal Engine Bot (Multi-Timeframe)...")
    app = create_bot_application()
    app.run_polling()


if __name__ == "__main__":
    main()
