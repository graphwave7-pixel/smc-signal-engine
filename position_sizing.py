def calculate_position_size(
    capital: float,
    risk_percent: float = 1.0,
    entry: float = None,
    stop_loss: float = None,
    lot_size: int = 25,
    is_option: bool = False,
    option_premium: float = None
):
    if entry is None or stop_loss is None:
        return {
            "error": "Entry and Stop Loss are required",
            "quantity": 0,
            "risk_amount": 0
        }

    risk_amount = capital * (risk_percent / 100)

    if is_option and option_premium is not None:
        max_premium_risk = risk_amount
        quantity = int(max_premium_risk / option_premium)
        quantity = (quantity // lot_size) * lot_size
        actual_risk = quantity * option_premium
    else:
        points_at_risk = abs(entry - stop_loss)
        if points_at_risk == 0:
            return {"error": "Entry and SL cannot be same", "quantity": 0}

        raw_quantity = risk_amount / points_at_risk
        quantity = int(raw_quantity)
        quantity = (quantity // lot_size) * lot_size
        actual_risk = quantity * points_at_risk

    return {
        "capital": capital,
        "risk_percent": risk_percent,
        "risk_amount_planned": round(risk_amount, 2),
        "actual_risk": round(actual_risk, 2),
        "quantity": quantity,
        "lot_size": lot_size,
        "points_at_risk": round(abs(entry - stop_loss), 2) if not is_option else None,
        "is_option": is_option
    }


def calculate_rr_and_pnl(entry, stop_loss, target1, target2, quantity, is_option=False, premium=None):
    if entry is None or stop_loss is None:
        return None

    risk_points = abs(entry - stop_loss)

    if is_option and premium:
        risk_amount = quantity * premium
        reward1 = quantity * (target1 - premium) if target1 else None
        reward2 = quantity * (target2 - premium) if target2 else None
    else:
        risk_amount = quantity * risk_points
        reward1 = quantity * abs(target1 - entry) if target1 else None
        reward2 = quantity * abs(target2 - entry) if target2 else None

    rr1 = round(reward1 / risk_amount, 2) if reward1 and risk_amount > 0 else None
    rr2 = round(reward2 / risk_amount, 2) if reward2 and risk_amount > 0 else None

    return {
        "risk_amount": round(risk_amount, 2),
        "potential_profit_t1": round(reward1, 2) if reward1 else None,
        "potential_profit_t2": round(reward2, 2) if reward2 else None,
        "rr_t1": rr1,
        "rr_t2": rr2
  }
