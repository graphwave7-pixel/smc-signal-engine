from datetime import datetime, time
import pytz

IST = pytz.timezone("Asia/Kolkata")

def is_in_kill_zone(current_time: datetime = None) -> dict:
    if current_time is None:
        current_time = datetime.now(IST)
    else:
        if current_time.tzinfo is None:
            current_time = IST.localize(current_time)

    current = current_time.time()

    market_open_avoid_start = time(9, 15)
    market_open_avoid_end   = time(9, 40)

    european_window_start   = time(12, 30)
    european_window_end     = time(13, 45)

    late_day_avoid_start    = time(15, 0)

    in_avoid_open = market_open_avoid_start <= current <= market_open_avoid_end
    in_european   = european_window_start <= current <= european_window_end
    in_late_avoid = current >= late_day_avoid_start

    if in_european:
        status = "GOOD"
        reason = "Inside European Open Kill Zone (preferred window)"
        allow_trade = True
    elif in_avoid_open:
        status = "AVOID"
        reason = "First 25 minutes after market open – high volatility"
        allow_trade = False
    elif in_late_avoid:
        status = "AVOID"
        reason = "Last part of the day – avoid new entries"
        allow_trade = False
    else:
        status = "NEUTRAL"
        reason = "Outside preferred Kill Zone"
        allow_trade = False

    return {
        "status": status,
        "allow_trade": allow_trade,
        "reason": reason,
        "current_time": current_time.strftime("%H:%M:%S"),
        "preferred_window": "12:30 – 13:45 IST"
    }


def apply_kill_zone_filter(signal: dict) -> dict:
    kz = is_in_kill_zone()
    signal["kill_zone"] = kz

    if signal["decision"] == "ENTER" and not kz["allow_trade"]:
        signal["decision"] = "DO NOT ENTER"
        if "reason" not in signal or not isinstance(signal["reason"], list):
            signal["reason"] = []
        signal["reason"].append(f"Kill Zone Filter: {kz['reason']}")
    
    return signal
