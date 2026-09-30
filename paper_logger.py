import json
from datetime import datetime
import os

LOG_FILE = "paper_trades.json"

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

    print(f"Trade logged: {trade['decision']} - {trade['instrument']}")


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

    # Simple potential P&L calculation (only from ENTER signals)
    total_potential_profit = 0
    total_risk = 0

    for t in enter_signals:
        if t.get("potential_profit_t1"):
            total_potential_profit += t["potential_profit_t1"]
        if t.get("risk_amount"):
            total_risk += t["risk_amount"]

    summary = (
        f"📊 *Paper Trading Summary*\n\n"
        f"Total Signals: {total_signals}\n"
        f"ENTER Signals: {total_enter}\n"
        f"DO NOT ENTER: {total_skipped}\n\n"
        f"Total Risk Taken: ₹{round(total_risk, 2)}\n"
        f"Potential Profit (T1): ₹{round(total_potential_profit, 2)}\n\n"
        f"_Note: This is paper trading only. Real P&L will depend on actual execution._"
    )

    return summary
