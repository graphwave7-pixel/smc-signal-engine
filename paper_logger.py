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
