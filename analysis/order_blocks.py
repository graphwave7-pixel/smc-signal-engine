import pandas as pd
import numpy as np
from analysis.market_structure import find_swing_points

def detect_fair_value_gaps(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Bullish_FVG'] = False
    df['Bearish_FVG'] = False
    df['FVG_Top'] = np.nan
    df['FVG_Bottom'] = np.nan

    for i in range(2, len(df)):
        # Bullish FVG
        if df['Low'].iloc[i] > df['High'].iloc[i-2]:
            df.iloc[i, df.columns.get_loc('Bullish_FVG')] = True
            df.iloc[i, df.columns.get_loc('FVG_Top')] = df['Low'].iloc[i]
            df.iloc[i, df.columns.get_loc('FVG_Bottom')] = df['High'].iloc[i-2]

        # Bearish FVG
        if df['High'].iloc[i] < df['Low'].iloc[i-2]:
            df.iloc[i, df.columns.get_loc('Bearish_FVG')] = True
            df.iloc[i, df.columns.get_loc('FVG_Top')] = df['Low'].iloc[i-2]
            df.iloc[i, df.columns.get_loc('FVG_Bottom')] = df['High'].iloc[i]

    return df


def detect_order_blocks(df: pd.DataFrame, min_body_ratio: float = 0.6) -> pd.DataFrame:
    df = detect_fair_value_gaps(df)
    df = df.copy()

    df['Bullish_OB'] = False
    df['Bearish_OB'] = False
    df['OB_Top'] = np.nan
    df['OB_Bottom'] = np.nan

    for i in range(2, len(df)):
        c0 = df.iloc[i-2]
        c1 = df.iloc[i-1]
        c2 = df.iloc[i]

        body_c1 = abs(c1['Close'] - c1['Open'])
        range_c1 = c1['High'] - c1['Low']
        body_ratio = body_c1 / range_c1 if range_c1 != 0 else 0

        # Bullish Order Block
        if (c1['Close'] > c1['Open'] and 
            body_ratio >= min_body_ratio and
            c2['Bullish_FVG']):

            df.iloc[i-2, df.columns.get_loc('Bullish_OB')] = True
            df.iloc[i-2, df.columns.get_loc('OB_Top')] = c0['High']
            df.iloc[i-2, df.columns.get_loc('OB_Bottom')] = c0['Low']

        # Bearish Order Block
        if (c1['Close'] < c1['Open'] and 
            body_ratio >= min_body_ratio and
            c2['Bearish_FVG']):

            df.iloc[i-2, df.columns.get_loc('Bearish_OB')] = True
            df.iloc[i-2, df.columns.get_loc('OB_Top')] = c0['High']
            df.iloc[i-2, df.columns.get_loc('OB_Bottom')] = c0['Low']

    return df


def get_latest_order_blocks(df: pd.DataFrame, lookback: int = 30) -> dict:
    df = detect_order_blocks(df)
    recent = df.tail(lookback)

    bullish_obs = recent[recent['Bullish_OB'] == True]
    bearish_obs = recent[recent['Bearish_OB'] == True]

    latest_bullish = None
    latest_bearish = None

    if not bullish_obs.empty:
        last = bullish_obs.iloc[-1]
        latest_bullish = {
            "top": float(last['OB_Top']),
            "bottom": float(last['OB_Bottom']),
            "time": str(last.name)
        }

    if not bearish_obs.empty:
        last = bearish_obs.iloc[-1]
        latest_bearish = {
            "top": float(last['OB_Top']),
            "bottom": float(last['OB_Bottom']),
            "time": str(last.name)
        }

    bullish_fvgs = recent[recent['Bullish_FVG'] == True]
    bearish_fvgs = recent[recent['Bearish_FVG'] == True]

    latest_bullish_fvg = None
    latest_bearish_fvg = None

    if not bullish_fvgs.empty:
        last = bullish_fvgs.iloc[-1]
        latest_bullish_fvg = {
            "top": float(last['FVG_Top']),
            "bottom": float(last['FVG_Bottom'])
        }

    if not bearish_fvgs.empty:
        last = bearish_fvgs.iloc[-1]
        latest_bearish_fvg = {
            "top": float(last['FVG_Top']),
            "bottom": float(last['FVG_Bottom'])
        }

    return {
        "bullish_order_block": latest_bullish,
        "bearish_order_block": latest_bearish,
        "bullish_fvg": latest_bullish_fvg,
        "bearish_fvg": latest_bearish_fvg
          }
