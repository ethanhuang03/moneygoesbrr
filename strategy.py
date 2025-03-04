def sample_strategy(price_data, indicators_result: dict):
    """
    A sample strategy that uses MACD, ADX, and RSI (if enabled) to generate buy/sell signals.
    `data` is a dict with key "close" (numpy array).
    `indicators_result` is a dict with computed indicator arrays (e.g., "MACD", "MACD_Signal", "ADX", "RSI").
    Returns:
       x_buy, y_buy, x_sell, y_sell: arrays of indices and prices where buy/sell signals occur.
    """
    print(indicators_result.keys())
    try:
        close = price_data["close"]
        date = price_data["date"]
        
        # Unpack required indicators if available.
        ema = indicators_result.get("ema")[1][0]
        macd = indicators_result.get("macd")[1][0]
        macd_signal = indicators_result.get("macd")[1][1]
        macd_hist = indicators_result.get("macd")[1][2]
        rsi = indicators_result.get("rsi")[1][0]
        adx = indicators_result.get("adx")[1][0]

        print("Sample Strategy Loaded")

        common_length = min(len(close), len(date), len(ema), len(macd), len(macd_signal), len(macd_hist), len(rsi), len(adx))

        # Align arrays to common length
        close_common = close[-common_length:]
        ema_common = ema[-common_length:]
        macd_common = macd[-common_length:]
        macd_signal_common = macd_signal[-common_length:]
        macd_hist_common = macd_hist[-common_length:]
        rsi_common = rsi[-common_length:]
        adx_common = adx[-common_length:]
        date_common = date[-common_length:]  

        # Strat
        buy_condition = (
            (macd_common > macd_signal_common) &
            (macd_signal_common < 0) &
            (adx_common >= 20) &
            (rsi_common <= 40)
        )

        sell_condition = (
            (macd_common < macd_signal_common) &
            (macd_signal_common > 0) &
            (adx_common >= 20) &
            (rsi_common >= 60)
        )

        x_buy = date_common[buy_condition]
        y_buy = close_common[buy_condition]
        x_sell = date_common[sell_condition]
        y_sell = close_common[sell_condition]

        return x_buy, y_buy, x_sell, y_sell
    except:
        return None