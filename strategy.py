from submodules.indicators import compute_indicator, indicator_info
import numpy as np


class BaseStrategy:
    def __init__(self, price_data, computed_indicators, indicator_params):
        """
        price_data: dict of price arrays.
        computed_indicators: dict of already computed indicators.
        indicator_params: dict of indicator parameters provided by the user.
        """
        self.price_data = price_data
        # Use a copy so we don’t overwrite external computed indicators.
        self.computed_indicators = computed_indicators.copy()
        self.indicator_params = indicator_params
        self.ensure_indicators_loaded()

    def ensure_indicators_loaded(self):
        """
        For each required indicator (defined in required_indicators),
        compute it if not already available. Use user-provided parameters if available.
        """
        required = self.required_indicators()
        for ind, default_params in required.items():
            if ind not in self.computed_indicators:
                params = self.indicator_params.get(ind, default_params)
                try:
                    self.computed_indicators[ind] = compute_indicator(ind, self.price_data, params)
                except Exception as e:
                    print(f"Could not compute {ind}: {e}")
                    print(f"Input params: {params}")
                    print(f"Indicator options: {indicator_info(ind)['Options']}")                

    def required_indicators(self):
        """
        Should return a dictionary of required indicators and their default parameters.
        e.g. {"ema": {"period": 14}, ...}
        Override this method in subclasses.
        """
        raise NotImplementedError

    def align_data(self, arrays):
        """
        Align multiple arrays based on the minimum length among them.
        Returns the aligned arrays.
        """
        min_len = min(len(a) for a in arrays)
        return [a[-min_len:] for a in arrays]

    def generate_signals(self):
        """
        Override this method to implement strategy logic.
        Should return strategy signals (x_buy, y_buy, x_sell, y_sell).
        """
        raise NotImplementedError


class SampleStrategy(BaseStrategy):
    def required_indicators(self):
        # Define required indicators for the sample strategy with default parameters.
        return {
            "ema": {"period": 200},
            "macd": {"short period": 12, "long period": 26, "signal period": 9},
            "rsi": {"period": 14},
            "adx": {"period": 14}
        }
    
    def generate_signals(self):
        try:
            close = self.price_data["close"]
            date = self.price_data["date"]

            ema = self.computed_indicators["ema"][1][0]
            macd = self.computed_indicators["macd"][1][0]
            macd_signal = self.computed_indicators["macd"][1][1]
            macd_hist = self.computed_indicators["macd"][1][2]
            rsi = self.computed_indicators["rsi"][1][0]
            adx = self.computed_indicators["adx"][1][0]

            # Align all arrays so that their lengths match
            close, date, ema, macd, macd_signal, macd_hist, rsi, adx = self.align_data(
                [close, date, ema, macd, macd_signal, macd_hist, rsi, adx]
            )

            # Define strategy conditions (buy and sell conditions)
            buy_condition = (
                (macd > macd_signal) &
                (macd_signal < 0) &
                (adx >= 20) &
                (rsi <= 40)
            )
            sell_condition = (
                (macd < macd_signal) &
                (macd_signal > 0) &
                (adx >= 20) &
                (rsi >= 60)
            )

            x_buy = date[buy_condition]
            y_buy = close[buy_condition]
            x_sell = date[sell_condition]
            y_sell = close[sell_condition]

            return x_buy, y_buy, x_sell, y_sell
        except Exception as e:
            print(f"Error generating signals: {e}")
            return None
