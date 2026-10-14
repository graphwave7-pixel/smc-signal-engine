def suggest_option(direction: str, spot_price: float, instrument: str = "Nifty"):
    """
    Suggest ATM option and estimate premium + cost for 1 lot
    """

    if instrument.lower() == "nifty":
        step = 50
        lot_size = 25
        # Rough ATM premium estimation (very approximate)
        base_premium = max(80, spot_price * 0.006)
    else:  # BankNifty
        step = 100
        lot_size = 15
        base_premium = max(150, spot_price * 0.006)

    # Round to nearest strike
    atm_strike = round(spot_price / step) * step

    if direction.lower() == "bullish":
        option_type = "CE"
        recommended = f"{instrument.upper()} {int(atm_strike)} CE"
    else:
        option_type = "PE"
        recommended = f"{instrument.upper()} {int(atm_strike)} PE"

    estimated_premium = round(base_premium, 1)
    cost_for_1_lot = round(estimated_premium * lot_size, 2)

    # Approximate option levels (using rough delta 0.5 for ATM)
    # This is only estimation
    index_entry = spot_price
    index_sl_distance = 40 if instrument.lower() == "nifty" else 70

    option_entry = estimated_premium
    option_sl = round(estimated_premium * 0.65, 1)          # \~35% SL
    option_t1 = round(estimated_premium * 1.6, 1)           # \~60% target
    option_t2 = round(estimated_premium * 2.1, 1)           # \~110% target

    return {
        "recommended": recommended,
        "strike": int(atm_strike),
        "option_type": option_type,
        "estimated_premium": estimated_premium,
        "cost_1_lot": cost_for_1_lot,
        "lot_size": lot_size,
        "option_entry": option_entry,
        "option_sl": option_sl,
        "option_t1": option_t1,
        "option_t2": option_t2
        }
