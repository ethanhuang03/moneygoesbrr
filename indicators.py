import tulipy as ti
import inspect
import numpy as np


def get_available_indicators():
    """
    Return a dictionary of available indicators from tulipy.
    Each key is the indicator name and its value is a dictionary with:
      - 'function': the tulipy function
      - 'parameters': a dict mapping parameter names to default values (if available)
      - 'display': recommended display type ("overlay" or "separate")
    """
    indicators = {}
    for name in dir(ti):
        if not name.startswith("_"):
            func = getattr(ti, name)
            if callable(func):
                try:
                    sig = inspect.signature(func)
                    if len(sig.parameters) > 0:
                        params = {}
                        for param_name, param in sig.parameters.items():
                            params[param_name] = param.default if param.default is not param.empty else None
                        overlay_indicators = {"ema", "sma", "wma", "bbands"}
                        display_type = "overlay" if name.lower() in overlay_indicators else "separate"
                        indicators[name] = {"function": func, "parameters": params, "display": display_type}
                except Exception:
                    continue
    return indicators


def compute_indicator(indicator_name: str, price_data: dict, additional_params: dict):
    """
    Compute the indicator result.
    price_data should be a dict with keys: open, high, low, close, volume (numpy arrays).
    additional_params_params is a dict of parameters for the indicator.
    """
    available = get_available_indicators()
    if indicator_name not in available:
        raise ValueError(f"Indicator {indicator_name} not found in tulipy indicators.")

    func = available[indicator_name]["function"]
    sig_params = available[indicator_name]["parameters"]
    args = []
    for param_name in sig_params.keys():
        if param_name == "real":
            args.append(price_data["close"])
        if param_name == "open":
            args.append(price_data["open"])
        if param_name == "high":
            args.append(price_data["high"])
        if param_name == "low":
            args.append(price_data["low"])
        if param_name == "close":
            args.append(price_data["close"])
        if param_name == "volume":
            args.append(price_data["volume"])
        if param_name in additional_params:
            args.append(additional_params[param_name])
        else:
            continue

    # Some tulipy functions return multiple outputs; let the caller handle them.
    result = func(*args)

    # Ensure result is a numpy array (or tuple of arrays)
    if isinstance(result, (list, tuple)):
        result = [np.array(x) for x in result]
    else:
        result = np.array(result)
    return result
