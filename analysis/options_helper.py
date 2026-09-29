def get_atm_strike(spot_price: float, strike_interval: int = 50) -> int:
    return int(round(spot_price / strike_interval) * strike_interval)


def suggest_option(direction: str, spot_price: float, instrument: str = "Nifty", preferred: str = "ATM"):
    if instrument.lower() == "nifty":
        interval = 50
        lot_size = 25
        symbol_prefix = "NIFTY"
    elif instrument.lower() == "banknifty":
        interval = 100
        lot_size = 15
        symbol_prefix = "BANKNIFTY"
    else:
        interval = 50
        lot_size = 25
        symbol_prefix = instrument.upper()

    atm_strike = get_atm_strike(spot_price, interval)

    if direction == "Bullish":
        option_type = "CE"
        strike = atm_strike
        action = "BUY"
    elif direction == "Bearish":
        option_type = "PE"
        strike = atm_strike
        action = "BUY"
    else:
        return {"error": "Direction must be Bullish or Bearish"}

    estimated_premium = round(spot_price * 0.006, 1)

    return {
        "instrument": instrument,
        "direction": direction,
        "action": action,
        "option_type": option_type,
        "strike": strike,
        "strike_type": "ATM",
        "recommended": f"{symbol_prefix} {strike} {option_type}",
        "lot_size": lot_size,
        "estimated_premium": estimated_premium,
        "note": "Premium is approximate. Use live option chain for exact price."
  }
