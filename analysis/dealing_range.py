import pandas as pd
from analysis.market_structure import find_swing_points

def calculate_dealing_range(df: pd.DataFrame, lookback: int = 40) -> dict:
    df = find_swing_points(df)
    recent = df.tail(lookback)

    swing_highs = recent['Swing_High'].dropna()
    swing_lows = recent['Swing_Low'].dropna()

    if len(swing_highs) == 0 or len(swing_lows) == 0:
        return {
            "range_high": None,
            "range_low": None,
            "equilibrium": None,
            "premium_zone": None,
            "discount_zone": None,
            "current_zone": "unknown",
            "current_price": None
        }

    range_high = float(swing_highs.max())
    range_low = float(swing_lows.min())
    equilibrium = (range_high + range_low) / 2
    current_price = float(df['Close'].iloc[-1])

    if current_price >= equilibrium:
        current_zone = "premium"
    else:
        current_zone = "discount"

    return {
        "range_high": range_high,
        "range_low": range_low,
        "equilibrium": round(equilibrium, 2),
        "premium_zone": f"{round(equilibrium, 2)} - {range_high}",
        "discount_zone": f"{range_low} - {round(equilibrium, 2)}",
        "current_zone": current_zone,
        "current_price": current_price
  }
