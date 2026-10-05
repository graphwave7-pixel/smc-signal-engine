import json
from datetime import datetime
import os

LOG_FILE = "paper_trades.json"
ACTIVE_TRADE_FILE = "active_trade.json"
CLOSED_TRADES_FILE = "closed_trades.json"

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

    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []

    logs.append(trade)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

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
            "lots": 0,
            "risk_amount": trade.get("risk_amount", 0)
        }
        with open(ACTIVE_TRADE_FILE, "w") as f:
            json.dump(active, f, indent=4)

    print(f"Trade logged: {trade['decision']} - {trade['instrument']}")


def record_taken_trade(lots: int) -> str:
    if not os.path.exists(ACTIVE_TRADE_FILE):
        return "No active ENTER signal found."

    with open(ACTIVE_TRADE_FILE, "r") as f:
        active = json.load(f)

    if active.get("taken"):
        return "This trade is already recorded."

    active["taken"] = True
    active["lots"] = lots
    active["taken_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(ACTIVE_TRADE_FILE, "w") as f:
        json.dump(active, f, indent=4)

    return (
        f"✅ Trade Recorded!\n\n"
        f"Instrument: {active['instrument']}\n"
        f"Direction: {active['direction']}\n"
        f"Lots: {lots}\n"
        f"Entry: {active['entry']}\n"
        f"SL: {active['stop_loss']}\n"
        f"Target 1: {active['target_1']}\n\n"
        f"When trade is over, use:\n"
        f"/close win\n"
        f"/close loss"
    )


def close_trade(result: str) -> str:
    if not os.path.exists(ACTIVE_TRADE_FILE):
        return "No active trade found."

    with open(ACTIVE_TRADE_FILE, "r") as f:
        active = json.load(f)

    if not active.get("taken"):
        return "You have not taken this trade yet. Use /take 1 or /take 2 first."

    risk = active.get("risk_amount", 1000)
    lots = active.get("lots", 1)

    if result.lower() == "win":
        pnl = risk * 2 * lots   # Assuming 1:2 RR
        status = "WIN"
    else:
        pnl = -risk * lots
        status = "LOSS"

    closed_trade = {
        "timestamp": active.get("timestamp"),
        "closed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "instrument": active.get("instrument"),
        "direction": active.get("direction"),
        "entry": active.get("entry"),
        "lots": lots,
        "result": status,
        "pnl": round(pnl, 2)
    }

    closed = []
    if os.path.exists(CLOSED_TRADES_FILE):
        with open(CLOSED_TRADES_FILE, "r") as f:
            try:
                closed = json.load(f)
            except:
                closed = []

    closed.append(closed_trade)

    with open(CLOSED_TRADES_FILE, "w") as f:
        json.dump(closed, f, indent=4)

    # Clear active trade
    if os.path.exists(ACTIVE_TRADE_FILE):
        os.remove(ACTIVE_TRADE_FILE)

    return (
        f"Trade Closed as {status}\n\n"
        f"Instrument: {closed_trade['instrument']}\n"
        f"Lots: {lots}\n"
        f"P&L: ₹{closed_trade['pnl']}"
    )


def get_summary() -> str:
    total_signals = 0
    enter_count = 0
    skipped_count = 0

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
                total_signals = len(logs)
                enter_count = len([t for t in logs if t.get("decision") == "ENTER"])
                skipped_count = total_signals - enter_count
            except:
                pass

    closed = []
    if os.path.exists(CLOSED_TRADES_FILE):
        with open(CLOSED_TRADES_FILE, "r") as f:
            try:
                closed = json.load(f)
            except:
                closed = []

    total_closed = len(closed)
    wins = len([t for t in closed if t.get("result") == "WIN"])
    losses = len([t for t in closed if t.get("result") == "LOSS"])

    win_rate = round((wins / total_closed) * 100, 1) if total_closed > 0 else 0
    total_pnl = sum([t.get("pnl", 0) for t in closed])

    # Simple Max Drawdown calculation
    max_drawdown = 0
    peak = 0
    equity = 0
    for t in closed:
        equity += t.get("pnl", 0)
        if equity > peak:
            peak = equity
        drawdown = peak - equity
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    active_text = "No active trade"
    if os.path.exists(ACTIVE_TRADE_FILE):
        with open(ACTIVE_TRADE_FILE, "r") as f:
            active = json.load(f)
        if active.get("taken"):
            active_text = (
                f"{active.get('instrument')} | {active.get('direction')} | "
                f"Lots: {active.get('lots')} | Entry: {active.get('entry')}"
            )

    summary = (
        f"📊 *Performance Summary*\n\n"
        f"*Signals*\n"
        f"Total Signals: {total_signals}\n"
        f"ENTER: {enter_count}\n"
        f"DO NOT ENTER: {skipped_count}\n\n"
        f"*Closed Trades*\n"
        f"Total Closed: {total_closed}\n"
        f"Wins: {wins}\n"
        f"Losses: {losses}\n"
        f"Win Rate: {win_rate}%\n\n"
        f"*Money*\n"
        f"Total P&L: ₹{round(total_pnl, 2)}\n"
        f"Max Drawdown: ₹{round(max_drawdown, 2)}\n\n"
        f"*Active Trade*\n"
        f"{active_text}"
    )

    return summary
