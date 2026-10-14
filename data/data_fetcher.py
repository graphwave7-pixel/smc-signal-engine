import yfinance as yf
import pandas as pd

def get_data(symbol: str, interval: str = "15m", period: str = "5d"):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(interval=interval, period=period)
        
        if df.empty:
            return None
            
        df = df.reset_index()
        
        # Keep original column names that analysis modules expect
        # yfinance usually gives: Open, High, Low, Close, Volume
        
        # Make sure we have the required columns
        required = ['Open', 'High', 'Low', 'Close']
        for col in required:
            if col not in df.columns:
                # Try lowercase version
                lower_col = col.lower()
                if lower_col in df.columns:
                    df.rename(columns={lower_col: col}, inplace=True)
                else:
                    return None
                
        return df
    except Exception as e:
        print(f"Error fetching {symbol} {interval}: {e}")
        return None


def get_nifty_data(interval="15m", period="5d"):
    return get_data("^NSEI", interval=interval, period=period)


def get_banknifty_data(interval="15m", period="5d"):
    return get_data("^NSEBANK", interval=interval, period=period)


def get_multi_tf_data(instrument="Nifty"):
    """
    Returns data for multiple timeframes
    """
    if instrument.lower() == "nifty":
        symbol = "^NSEI"
    else:
        symbol = "^NSEBANK"

    data = {
        "5m": get_data(symbol, interval="5m", period="5d"),
        "15m": get_data(symbol, interval="15m", period="10d"),
        "1h": get_data(symbol, interval="1h", period="1mo"),
    }
    return data
