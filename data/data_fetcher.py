import yfinance as yf
import pandas as pd

def get_index_data(symbol: str, interval: str = "15m", period: str = "5d") -> pd.DataFrame:
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    
    if df.empty:
        raise ValueError(f"No data received for {symbol}")
    
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    df.index = pd.to_datetime(df.index)
    df = df.tz_localize(None)
    
    return df

def get_nifty_data(interval="15m", period="5d"):
    return get_index_data("^NSEI", interval, period)

def get_banknifty_data(interval="15m", period="5d"):
    return get_index_data("^NSEBANK", interval, period)
