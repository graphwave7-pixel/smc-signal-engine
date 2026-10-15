import yfinance as yf
import pandas as pd

def get_stock_data(symbol: str, period="3mo", interval="1d"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        if df.empty:
            return None
        df = df.reset_index()
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def generate_swing_signal(symbol: str):
    """
    Simple Swing Trading signal based on:
    - Trend (Higher High / Higher Low or Lower High / Lower Low)
    - Moving Averages
    - Recent strength
    """
    df = get_stock_data(symbol)
    
    if df is None or len(df) < 50:
        return {
            "symbol": symbol.replace(".NS", ""),
            "decision": "DO NOT ENTER",
            "reason": ["Not enough data"]
        }

    df['SMA20'] = df['Close'].rolling(20).mean()
    df['SMA50'] = df['Close'].rolling(50).mean()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    current_price = float(last['Close'])
    sma20 = float(last['SMA20'])
    sma50 = float(last['SMA50'])

    decision = "DO NOT ENTER"
    direction = None
    reason = []
    entry = None
    stop_loss = None
    target1 = None

    # Bullish Swing Conditions
    if current_price > sma20 > sma50:
        # Price above both MAs → Uptrend
        if last['Close'] > prev['Close']:
            decision = "ENTER"
            direction = "Bullish"
            entry = round(current_price, 2)
            stop_loss = round(min(last['Low'], sma20) * 0.98, 2)
            risk = entry - stop_loss
            target1 = round(entry + (risk * 2), 2)
            reason = [
                "Price above 20 & 50 SMA",
                "Uptrend structure",
                "Bullish momentum"
            ]

    # Bearish Swing Conditions
    elif current_price < sma20 < sma50:
        if last['Close'] < prev['Close']:
            decision = "ENTER"
            direction = "Bearish"
            entry = round(current_price, 2)
            stop_loss = round(max(last['High'], sma20) * 1.02, 2)
            risk = stop_loss - entry
            target1 = round(entry - (risk * 2), 2)
            reason = [
                "Price below 20 & 50 SMA",
                "Downtrend structure",
                "Bearish momentum"
            ]
    else:
        reason = ["No clear swing trend"]

    return {
        "symbol": symbol.replace(".NS", ""),
        "decision": decision,
        "direction": direction,
        "entry": entry,
        "stop_loss": stop_loss,
        "target_1": target1,
        "reason": reason,
        "current_price": round(current_price, 2)
  }
