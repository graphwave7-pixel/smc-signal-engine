import pandas as pd
import numpy as np

def find_swing_points(df: pd.DataFrame, left: int = 3, right: int = 3) -> pd.DataFrame:
    df = df.copy()
    df['Swing_High'] = np.nan
    df['Swing_Low'] = np.nan

    highs = df['High'].values
    lows = df['Low'].values

    for i in range(left, len(df) - right):
        if highs[i] == max(highs[i-left : i+right+1]):
            df.iloc[i, df.columns.get_loc('Swing_High')] = highs[i]
        if lows[i] == min(lows[i-left : i+right+1]):
            df.iloc[i, df.columns.get_loc('Swing_Low')] = lows[i]

    return df


def detect_bos_choch(df: pd.DataFrame) -> pd.DataFrame:
    df = find_swing_points(df)
    df = df.copy()

    df['BOS_Bullish'] = False
    df['BOS_Bearish'] = False
    df['CHoCH_Bullish'] = False
    df['CHoCH_Bearish'] = False
    df['Trend'] = None

    last_swing_high = None
    last_swing_low = None
    trend = None

    for i in range(len(df)):
        row = df.iloc[i]

        if not pd.isna(row['Swing_High']):
            if last_swing_high is not None and row['Close'] > last_swing_high:
                if trend == "bearish":
                    df.iloc[i, df.columns.get_loc('CHoCH_Bullish')] = True
                    trend = "bullish"
                else:
                    df.iloc[i, df.columns.get_loc('BOS_Bullish')] = True
                    trend = "bullish"
            last_swing_high = row['Swing_High']

        if not pd.isna(row['Swing_Low']):
            if last_swing_low is not None and row['Close'] < last_swing_low:
                if trend == "bullish":
                    df.iloc[i, df.columns.get_loc('CHoCH_Bearish')] = True
                    trend = "bearish"
                else:
                    df.iloc[i, df.columns.get_loc('BOS_Bearish')] = True
                    trend = "bearish"
            last_swing_low = row['Swing_Low']

        df.iloc[i, df.columns.get_loc('Trend')] = trend

    return df


def get_current_bias(df: pd.DataFrame) -> dict:
    df = detect_bos_choch(df)
    latest = df.iloc[-1]

    bias = latest['Trend'] if latest['Trend'] else "sideways"

    return {
        "bias": bias,
        "last_bos_bullish": bool(latest['BOS_Bullish']),
        "last_bos_bearish": bool(latest['BOS_Bearish']),
        "last_choch_bullish": bool(latest['CHoCH_Bullish']),
        "last_choch_bearish": bool(latest['CHoCH_Bearish']),
        "last_close": latest['Close']
      }
