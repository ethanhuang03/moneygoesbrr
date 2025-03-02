import numpy as np

def sample_strategy(data, indicators_result: dict):
    """
    A sample strategy that uses MACD, ADX, and RSI (if enabled) to generate buy/sell signals.
    `data` is a dict with key "close" (numpy array).
    `indicators_result` is a dict with computed indicator arrays (e.g., "MACD", "MACD_Signal", "ADX", "RSI").
    Returns:
       x_buy, y_buy, x_sell, y_sell: arrays of indices and prices where buy/sell signals occur.
    """
    close = data["close"]
    # Unpack required indicators if available.
    macd = indicators_result.get("MACD")
    macd_signal = indicators_result.get("MACD_Signal")
    adx = indicators_result.get("ADX")
    rsi = indicators_result.get("RSI")
    
    # Find common length based on the shortest indicator array
    common_length = len(close)
    if macd is not None and macd_signal is not None:
        common_length = min(common_length, len(macd))
    if adx is not None:
        common_length = min(common_length, len(adx))
    if rsi is not None:
        common_length = min(common_length, len(rsi))
    
    # Align arrays to common length
    close_common = close[-common_length:]
    idx = np.arange(common_length)
    
    # Define buy and sell conditions
    # (These conditions are illustrative; you can adjust parameters in the UI.)
    if macd is not None and macd_signal is not None and adx is not None and rsi is not None:
        macd_common = macd[-common_length:]
        macd_signal_common = macd_signal[-common_length:]
        adx_common = adx[-common_length:]
        rsi_common = rsi[-common_length:]
    
        buy_condition = (
            (macd_common > macd_signal_common) &
            (macd_signal_common < 0) &
            (adx_common >= 20) &
            (rsi_common <= 40)
        )
    
        sell_condition = (
            (macd_common < macd_signal_common) &
            (macd_signal_common > 0) &
            (adx_common >= 40) &
            (rsi_common >= 60)
        )
    
        x_buy = idx[buy_condition]
        y_buy = close_common[buy_condition]
        x_sell = idx[sell_condition]
        y_sell = close_common[sell_condition]
    else:
        # If not all required indicators are available, no signals are generated.
        x_buy, y_buy, x_sell, y_sell = np.array([]), np.array([]), np.array([]), np.array([])

    return x_buy, y_buy, x_sell, y_sell
