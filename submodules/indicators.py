import tulipy as ti
import inspect
import numpy as np


def indicator_info(indicator_name: str):
    ind = getattr(ti, indicator_name)
    return {
        "function": ind,
        "Indicator Name": ind.full_name,
        "Type": ind.type,
        "Inputs": ind.inputs,
        "Options": ind.options,
        "Outputs": ind.outputs
    }


def get_valid_indicators():
    valid_indicators = []
    for ind in dir(ti):
        if inspect.isfunction(getattr(ti, ind)) and (getattr(ti, ind).type in ["indicator", "overlay"]):
            valid_indicators.append(ind)
    return valid_indicators
            

def compute_indicator(indicator_name: str, price_data: dict, additional_params: dict):
    """
    Compute the indicator result.
    price_data should be a dict with keys: open, high, low, close, volume (numpy arrays).
    additional_params_params is a dict of parameters for the indicator.
    """
    try:
        indicator = indicator_info(indicator_name)
    except:
        raise ValueError(f"Indicator {indicator_name} not found in tulipy indicators or has not been implemented.")

    args = []
    for i in indicator["Inputs"]:
        if i == "real":
            args.append(price_data["close"])
        else:
            args.append(price_data[i])
    for i in indicator["Options"]:
        args.append(additional_params[i])

    # Some tulipy functions return multiple outputs; let the caller handle them.
    result = indicator["function"](*args)
    
    # Ensure result is a numpy array (or tuple of arrays)
    if isinstance(result, (list, tuple)):
        result = [np.array(r) for r in result]
    else:
        result = [np.array(result)]
    return (indicator["Outputs"], result)
