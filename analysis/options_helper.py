from angel_data import get_option_ltp
from datetime import datetime, timedelta

def get_nearest_expiry_symbol(instrument: str, strike: int, option_type: str):
    """
    Create a possible trading symbol for Angel One.
    Note: Exact symbol format can vary. This is a common format.
    """
    today = datetime.now()
    
    # Find next Thursday (common weekly expiry)
    days_ahead = 3 - today.weekday()  # Thursday is 3
    if days_ahead <= 0:
        days_ahead += 7
    expiry = today + timedelta(days=days_ahead)
    
    # Format: BANKNIFTY24OCT2455200CE  or similar
    year = expiry.strftime("%y")
    month = expiry.strftime("%b").upper()
    day = expiry.strftime("%d")
    
    if instrument.upper() == "NIFTY":
        symbol = f"NIFTY{year}{month}{day}{strike}{option_type}"
    else:
        symbol = f"BANKNIFTY{year}{month}{day}{strike}{option_type}"
    
    return symbol


def suggest_option(direction: str, spot_price: float, instrument: str = "Nifty"):
    if instrument.lower() == "nifty":
        step = 50
        lot_size = 25
    else:
        step = 100
        lot_size = 15

    atm_strike = round(spot_price / step) * step

    if direction.lower() == "bullish":
        option_type = "CE"
    else:
        option_type = "PE"

    recommended = f"{instrument.upper()} {int(atm_strike)} {option_type}"

    # Try to get real LTP from Angel One
    tradingsymbol = get_nearest_expiry_symbol(instrument, int(atm_strike), option_type)
    real_ltp = get_option_ltp(tradingsymbol)

    if real_ltp is not None:
        estimated_premium = round(float(real_ltp), 1)
        source = "Live (Angel One)"
    else:
        # Fallback estimation
        estimated_premium = round(max(80, spot_price * 0.006), 1)
        source = "Estimated (fallback)"

    cost_for_1_lot = round(estimated_premium * lot_size, 2)

    # Approximate option levels
    option_entry = estimated_premium
    option_sl = round(estimated_premium * 0.70, 1)
    option_t1 = round(estimated_premium * 1.50, 1)
    option_t2 = round(estimated_premium * 2.00, 1)

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
        "option_t2": option_t2,
        "source": source,
        "tradingsymbol": tradingsymbol
    }
