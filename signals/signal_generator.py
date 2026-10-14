from analysis.market_structure import get_current_bias
from analysis.liquidity import get_liquidity_analysis
from analysis.order_blocks import get_latest_order_blocks
from analysis.dealing_range import calculate_dealing_range

def generate_signal(df_15m, instrument="Nifty", df_1h=None):
    """
    Multi-timeframe signal generator
    - 15m = Entry timeframe
    - 1h  = Higher timeframe bias confirmation
    """

    # Higher Timeframe Bias (1H)
    htf_bias = "neutral"
    if df_1h is not None and not df_1h.empty:
        try:
            htf_info = get_current_bias(df_1h)
            htf_bias = htf_info.get("bias", "neutral")
        except:
            htf_bias = "neutral"

    # 15-minute Analysis
    bias_info = get_current_bias(df_15m)
    bias = bias_info.get("bias", "neutral")

    liq = get_liquidity_analysis(df_15m)
    obs = get_latest_order_blocks(df_15m)
    dr = calculate_dealing_range(df_15m)

    decision = "DO NOT ENTER"
    reason = []
    direction = None
    entry = None
    stop_loss = None
    target1 = None
    target2 = None

    current_price = float(df_15m['Close'].iloc[-1])
    last_candle = df_15m.iloc[-1]

    # Displacement check
    body = abs(last_candle['Close'] - last_candle['Open'])
    candle_range = last_candle['High'] - last_candle['Low']
    body_ratio = body / candle_range if candle_range != 0 else 0

    has_bullish_displacement = last_candle['Close'] > last_candle['Open'] and body_ratio > 0.55
    has_bearish_displacement = last_candle['Close'] < last_candle['Open'] and body_ratio > 0.55

    # ==================== BULLISH SETUP ====================
    if bias == "bullish":
        direction = "Bullish"
        reasons_ok = []

        if htf_bias in ["bullish", "neutral"]:
            reasons_ok.append(f"1H Bias: {htf_bias}")
        else:
            reason.append(f"1H Bias is {htf_bias} (against trade)")

        if liq.get("liquidity_sweep") == "bullish" or liq.get("swept_sell_side"):
            reasons_ok.append("Sell-side Liquidity Sweep")
        else:
            reason.append("No Sell-side Liquidity Sweep")

        if obs.get("bullish_order_block") is not None:
            ob = obs["bullish_order_block"]
            ob_mid = (ob["top"] + ob["bottom"]) / 2
            distance = abs(current_price - ob_mid) / current_price

            if distance < 0.007:
                reasons_ok.append("Bullish Order Block nearby")
                entry = round(ob_mid, 2)
                stop_loss = round(ob["bottom"] - 20, 2)
            else:
                reason.append("Bullish Order Block too far")
        else:
            reason.append("No Bullish Order Block")

        if obs.get("bullish_fvg") is not None:
            reasons_ok.append("Bullish FVG present")
        else:
            reason.append("No Bullish FVG")

        if dr.get("current_zone") == "discount":
            reasons_ok.append("Price in Discount")
        else:
            reason.append("Not in Discount zone")

        if has_bullish_displacement:
            reasons_ok.append("Bullish Displacement")

        if len(reasons_ok) >= 3 and entry and stop_loss and entry > stop_loss:
            risk = entry - stop_loss
            target1 = round(entry + (risk * 2), 2)
            target2 = round(entry + (risk * 3), 2)
            decision = "ENTER"
            reason = reasons_ok

    # ==================== BEARISH SETUP ====================
    elif bias == "bearish":
        direction = "Bearish"
        reasons_ok = []

        if htf_bias in ["bearish", "neutral"]:
            reasons_ok.append(f"1H Bias: {htf_bias}")
        else:
            reason.append(f"1H Bias is {htf_bias} (against trade)")

        if liq.get("liquidity_sweep") == "bearish" or liq.get("swept_buy_side"):
            reasons_ok.append("Buy-side Liquidity Sweep")
        else:
            reason.append("No Buy-side Liquidity Sweep")

        if obs.get("bearish_order_block") is not None:
            ob = obs["bearish_order_block"]
            ob_mid = (ob["top"] + ob["bottom"]) / 2
            distance = abs(current_price - ob_mid) / current_price

            if distance < 0.007:
                reasons_ok.append("Bearish Order Block nearby")
                entry = round(ob_mid, 2)
                stop_loss = round(ob["top"] + 20, 2)
            else:
                reason.append("Bearish Order Block too far")
        else:
            reason.append("No Bearish Order Block")

        if obs.get("bearish_fvg") is not None:
            reasons_ok.append("Bearish FVG present")
        else:
            reason.append("No Bearish FVG")

        if dr.get("current_zone") == "premium":
            reasons_ok.append("Price in Premium")
        else:
            reason.append("Not in Premium zone")

        if has_bearish_displacement:
            reasons_ok.append("Bearish Displacement")

        if len(reasons_ok) >= 3 and entry and stop_loss and stop_loss > entry:
            risk = stop_loss - entry
            target1 = round(entry - (risk * 2), 2)
            target2 = round(entry - (risk * 3), 2)
            decision = "ENTER"
            reason = reasons_ok

    else:
        reason.append("No clear 15M bias")

    signal = {
        "instrument": instrument,
        "decision": decision,
        "direction": direction,
        "bias": bias,
        "htf_bias": htf_bias,
        "entry": entry,
        "stop_loss": stop_loss,
        "target_1": target1,
        "target_2": target2,
        "risk_reward_1": "1:2" if target1 else None,
        "risk_reward_2": "1:3" if target2 else None,
        "current_zone": dr.get("current_zone"),
        "reason": reason
    }

    return signal
