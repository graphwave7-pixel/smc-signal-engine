from analysis.market_structure import get_current_bias
from analysis.liquidity import get_liquidity_analysis
from analysis.order_blocks import get_latest_order_blocks
from analysis.dealing_range import calculate_dealing_range

def generate_signal(df, instrument="Nifty"):
    bias_info = get_current_bias(df)
    bias = bias_info["bias"]

    liq = get_liquidity_analysis(df)
    obs = get_latest_order_blocks(df)
    dr = calculate_dealing_range(df)

    decision = "DO NOT ENTER"
    reason = []
    direction = None
    entry = None
    stop_loss = None
    target1 = None
    target2 = None

    current_price = float(df['Close'].iloc[-1])
    last_candle = df.iloc[-1]
    prev_candle = df.iloc[-2]

    # Check for displacement (strong candle)
    body = abs(last_candle['Close'] - last_candle['Open'])
    candle_range = last_candle['High'] - last_candle['Low']
    body_ratio = body / candle_range if candle_range != 0 else 0

    has_bullish_displacement = last_candle['Close'] > last_candle['Open'] and body_ratio > 0.6
    has_bearish_displacement = last_candle['Close'] < last_candle['Open'] and body_ratio > 0.6

    # ==================== BULLISH SETUP ====================
    if bias == "bullish":
        direction = "Bullish"
        reasons_ok = []

        # 1. Liquidity Sweep compulsory
        if liq["liquidity_sweep"] == "bullish" or liq["swept_sell_side"]:
            reasons_ok.append("Sell-side Liquidity Sweep")
        else:
            reason.append("No Sell-side Liquidity Sweep")

        # 2. Bullish Order Block compulsory + price nearby
        if obs["bullish_order_block"] is not None:
            ob = obs["bullish_order_block"]
            ob_mid = (ob["top"] + ob["bottom"]) / 2
            distance = abs(current_price - ob_mid) / current_price

            if distance < 0.006:  # within 0.6%
                reasons_ok.append("Bullish Order Block nearby")
                entry = round(ob_mid, 2)
                stop_loss = round(ob["bottom"] - 25, 2)
            else:
                reason.append("Bullish Order Block too far")
        else:
            reason.append("No Bullish Order Block")

        # 3. Bullish FVG compulsory
        if obs["bullish_fvg"] is not None:
            reasons_ok.append("Bullish FVG present")
        else:
            reason.append("No Bullish FVG")

        # 4. Discount zone
        if dr["current_zone"] == "discount":
            reasons_ok.append("Price in Discount")
        else:
            reason.append("Not in Discount zone")

        # 5. Displacement (extra filter)
        if has_bullish_displacement:
            reasons_ok.append("Bullish Displacement")
        else:
            reason.append("No strong bullish displacement")

        # Need at least 4 strong reasons
        if len(reasons_ok) >= 4 and entry and stop_loss and (entry > stop_loss):
            risk = entry - stop_loss
            target1 = round(entry + (risk * 2), 2)
            target2 = round(entry + (risk * 3), 2)
            decision = "ENTER"
            reason = reasons_ok

    # ==================== BEARISH SETUP ====================
    elif bias == "bearish":
        direction = "Bearish"
        reasons_ok = []

        if liq["liquidity_sweep"] == "bearish" or liq["swept_buy_side"]:
            reasons_ok.append("Buy-side Liquidity Sweep")
        else:
            reason.append("No Buy-side Liquidity Sweep")

        if obs["bearish_order_block"] is not None:
            ob = obs["bearish_order_block"]
            ob_mid = (ob["top"] + ob["bottom"]) / 2
            distance = abs(current_price - ob_mid) / current_price

            if distance < 0.006:
                reasons_ok.append("Bearish Order Block nearby")
                entry = round(ob_mid, 2)
                stop_loss = round(ob["top"] + 25, 2)
            else:
                reason.append("Bearish Order Block too far")
        else:
            reason.append("No Bearish Order Block")

        if obs["bearish_fvg"] is not None:
            reasons_ok.append("Bearish FVG present")
        else:
            reason.append("No Bearish FVG")

        if dr["current_zone"] == "premium":
            reasons_ok.append("Price in Premium")
        else:
            reason.append("Not in Premium zone")

        if has_bearish_displacement:
            reasons_ok.append("Bearish Displacement")
        else:
            reason.append("No strong bearish displacement")

        if len(reasons_ok) >= 4 and entry and stop_loss and (stop_loss > entry):
            risk = stop_loss - entry
            target1 = round(entry - (risk * 2), 2)
            target2 = round(entry - (risk * 3), 2)
            decision = "ENTER"
            reason = reasons_ok

    else:
        reason.append("No clear bias")

    signal = {
        "instrument": instrument,
        "decision": decision,
        "direction": direction,
        "bias": bias,
        "entry": entry,
        "stop_loss": stop_loss,
        "target_1": target1,
        "target_2": target2,
        "risk_reward_1": "1:2" if target1 else None,
        "risk_reward_2": "1:3" if target2 else None,
        "current_zone": dr["current_zone"],
        "reason": reason,
        "liquidity": liq,
        "order_blocks": obs,
        "dealing_range": dr
    }

    return signal
