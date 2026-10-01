import json
from datetime import datetime
import os

LOG_FILE = "paper_trades.json"
ACTIVE_TRADE_FILE = "active_trade.json"

def log_trade(signal: dict, position: dict = None, pnl: dict = None):
    trade = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "instrument": signal.get("instrument"),
        "decision": signal.get("decision"),
        "direction": signal.get("direction"),
        "entry": signal.get("entry"),
        "stop_loss": signal.get("stop_loss"),
        "target_1": signal.get("target_1"),
        "target_2": signal.get("target_2"),
        "quantity": position.get("quantity") if position else None,
        "risk_amount": position.get("actual_risk") if position else None,
        "potential_profit_t1": pnl.get("potential_profit_t1") if pnl else None,
        "potential_profit_t2": pnl.get("potential_profit_t2") if pnl else None,
        "status": "open" if signal.get("decision") == "ENTER" else "skipped"
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    else:
        logs = []

    logs.append(trade)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

    # Save the latest ENTER signal as active trade
    if signal.get("decision") == "ENTER":
        active = {
            "timestamp": trade["timestamp"],
            "instrument": trade["instrument"],
            "direction": trade["direction"],
            "entry": trade["entry"],
            "stop_loss": trade["stop_loss"],
            "target_1": trade["target_1"],
            "target_2": trade["target_2"],
            "taken": False,
            "lots": 0
        }
        with open(ACTIVE_TRADE_FILE, "w") as f:
            json.dump(active, f, indent=4)

    print(f"Trade logged: {trade['decision']} - {trade['instrument']}")


def record_taken_trade(lots: int) -> str:
    if not os.path.exists(ACTIVE_TRADE_FILE):
        return "No active ENTER signal found. Wait for a new signal."

    with open(ACTIVE_TRADE_FILE, "r") as f:
        active = json.load(f)

    if active.get("taken"):
        return "You have already recorded this trade."

    active["taken"] = True
    active["lots"] = lots
    active["taken_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(ACTIVE_TRADE_FILE, "w") as f:
        json.dump(active, f, indent=4)

    return (
        f"✅ Trade Recorded Successfully!\n\n"
        f"Instrument: {active['instrument']}\n"
        f"Direction: {active['direction']}\n"
        f"Lots: {lots}\n"
        f"Entry: {active['entry']}\n"
        f"Stop Loss: {active['stop_loss']}\n"
        f"Target 1: {active['target_1']}\n\n"
        f"I will track this trade. You can check later with /summary"
    )


def get_summary() -> str:
    if not os.path.exists(LOG_FILE):
        return "No trades logged yet."

    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except:
        return "Could not read trade log."

    if not logs:
        return "No trades logged yet."

    total_signals = len(logs)
    enter_signals = [t for t in logs if t.get("decision") == "ENTER"]
    skipped_signals = [t for t in logs if t.get("decision") == "DO NOT ENTER"]

    total_enter = len(enter_signals)
    total_skipped = len(skipped_signals)

    total_potential_profit = 0
    total_risk = 0

    for t in enter_signals:
        if t.get("potential_profit_t1"):
            total_potential_profit += t["potential_profit_t1"]
        if t.get("risk_amount"):
            total_risk += t["risk_amount"]

    # Check active trade
    active_text = ""
    if os.path.exists(ACTIVE_TRADE_FILE):
        with open(ACTIVE_TRADE_FILE, "r") as f:
            active = json.load(f)
        if active.get("taken"):
            active_text = (
                f"\n\n📌 *Current Active Trade:*\n"
                f"Instrument: {active.get('instrument')}\n"
                f"Direction: {active.get('direction')}\n"
                f"Lots: {active.get('lots')}\n"
                f"Entry: {active.get('entry')}\n"
                f"SL: {active.get('stop_loss')}"
            )

    summary = (
        f"📊 *Paper Trading Summary*\n\n"
        f"Total Signals: {total_signals}\n"
        f"ENTER Signals: {total_enter}\n"
        f"DO NOT ENTER: {total_skipped}\n\n"
        f"Total Risk Taken: ₹{round(total_risk, 2)}\n"
        f"Potential Profit (T1): ₹{round(total_potential_profit, 2)}"
        f"{active_text}\n\n"
        f"_Note: This is paper trading only._"
    )

    return summary
