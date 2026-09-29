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

    if bias == "bullish":
        direction = "Bullish"
        reasons_ok = []

        if liq["liquidity_sweep"] == "bullish" or liq["swept_sell_side"]:
            reasons_ok.append("Liquidity Sweep (Sell-side)")
        else:
            reason.append("No bullish liquidity sweep")

        if obs["bullish_order_block"] is not None:
            reasons_ok.append("Valid Bullish Order Block")
            ob = obs["bullish_order_block"]
            entry = round((ob["top"] + ob["bottom"]) / 2, 2)
            stop_loss = round(ob["bottom"] - 15, 2)
        else:
            reason.append("No valid Bullish Order Block")

        if obs["bullish_fvg"] is not None:
            reasons_ok.append("Bullish FVG present")
        else:
            reason.append("No Bullish FVG")

        if dr["current_zone"] == "discount":
            reasons_ok.append("Price in Discount zone")
        else:
            reason.append("Price not in Discount zone")

        if len(reasons_ok) >= 3 and entry and stop_loss:
            risk = entry - stop_loss
            target1 = round(entry + (risk * 2), 2)
            target2 = round(entry + (risk * 3), 2)
            decision = "ENTER"
            reason = reasons_ok

    elif bias == "bearish":
        direction = "Bearish"
        reasons_ok = []

        if liq["liquidity_sweep"] == "bearish" or liq["swept_buy_side"]:
            reasons_ok.append("Liquidity Sweep (Buy-side)")
        else:
            reason.append("No bearish liquidity sweep")

        if obs["bearish_order_block"] is not None:
            reasons_ok.append("Valid Bearish Order Block")
            ob = obs["bearish_order_block"]
            entry = round((ob["top"] + ob["bottom"]) / 2, 2)
            stop_loss = round(ob["top"] + 15, 2)
        else:
            reason.append("No valid Bearish Order Block")

        if obs["bearish_fvg"] is not None:
            reasons_ok.append("Bearish FVG present")
        else:
            reason.append("No Bearish FVG")

        if dr["current_zone"] == "premium":
            reasons_ok.append("Price in Premium zone")
        else:
            reason.append("Price not in Premium zone")

        if len(reasons_ok) >= 3 and entry and stop_loss:
            risk = stop_loss - entry
            target1 = round(entry - (risk * 2), 2)
            target2 = round(entry - (risk * 3), 2)
            decision = "ENTER"
            reason = reasons_ok

    else:
        reason.append("No clear market bias (sideways)")

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
