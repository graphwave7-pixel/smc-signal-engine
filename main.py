import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

from data.data_fetcher import get_nifty_data, get_banknifty_data
from signals.signal_generator import generate_signal
from analysis.options_helper import suggest_option
from analysis.kill_zone import apply_kill_zone_filter
from position_sizing import calculate_position_size, calculate_rr_and_pnl
from bot import create_bot_application, send_signal_to_telegram
from paper_logger import log_trade

load_dotenv()

# ====== SETTINGS ======
CAPITAL = 100000
RISK_PERCENT = 1.0
NIFTY_LOT_SIZE = 25
BANKNIFTY_LOT_SIZE = 15


async def analyze_and_send(instrument: str = "Nifty"):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Analyzing {instrument}...")

    try:
        if instrument.lower() == "nifty":
            df = get_nifty_data(interval="15m", period="5d")
            lot_size = NIFTY_LOT_SIZE
        else:
            df = get_banknifty_data(interval="15m", period="5d")
            lot_size = BANKNIFTY_LOT_SIZE

        # Generate signal
        signal = generate_signal(df, instrument=instrument)

        # Apply Kill Zone filter
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
                lot_size=lot_size,
                is_option=False
            )

            pnl = calculate_rr_and_pnl(
                entry=signal["entry"],
                stop_loss=signal["stop_loss"],
                target1=signal.get("target_1"),
                target2=signal.get("target_2"),
                quantity=position["quantity"]
            )

        # Send to Telegram
        app = create_bot_application()
        await send_signal_to_telegram(
            application=app,
            signal=signal,
            option_suggestion=option_suggestion,
            position=position,
            pnl=pnl
        )

        # Paper trade log
        log_trade(signal, position, pnl)

        print(f"Signal sent for {instrument}: {signal['decision']}")

    except Exception as e:
        print(f"Error analyzing {instrument}: {e}")


async def main():
    await analyze_and_send("Nifty")
    await analyze_and_send("BankNifty")


if __name__ == "__main__":
    asyncio.run(main())
