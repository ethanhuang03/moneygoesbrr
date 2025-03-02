import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from submodules.data_retrieval import get_yfinance_data
from submodules.indicators import get_available_indicators, compute_indicator
from submodules.display import build_stock_chart


st.set_page_config(layout="wide", page_title="Stock Market Analysis Platform")

'''
In the future use an API to get the data
'''
ticker = st.sidebar.text_input("Ticker", "INTC")
start_date = st.sidebar.date_input("Start Date", datetime.today()-timedelta(days=90))
end_date = st.sidebar.date_input("End Date", datetime.today())
interval = st.sidebar.selectbox("Interval", ["1m", "2m", "5m", "15m", "30m", "90m", "1h", "1d", "1mo"])
start_datetime = datetime.combine(start_date, datetime.strptime("09:30", "%H:%M").time())
end_datetime = datetime.combine(end_date, datetime.strptime("16:30", "%H:%M").time())
df, date_index, open_arr, high_arr, low_arr, close_arr, volume_arr = get_yfinance_data(ticker, start_datetime, end_datetime, interval)

price_data = {
    "date": date_index,
    "open": open_arr,
    "high": high_arr,
    "low": low_arr,
    "close": close_arr,
    "volume": volume_arr
}

st.sidebar.header("Indicator Settings")
available_indicators = get_available_indicators()
enabled_indicators = st.sidebar.multiselect("Choose Indicators", list(available_indicators.keys()))

# For each enabled indicator, allow parameter adjustments
user_indicator_params = {}
for ind in enabled_indicators:
    st.sidebar.subheader(f"Settings for {ind}")
    default_params = available_indicators[ind]["parameters"]
    additional_params = {}
    for param_name, default in list(default_params.items()):
        if param_name not in ["real", "open", "high", "low", "close", "volume"]:
            if default is None:
                additional_params[param_name] = st.sidebar.number_input(f"{ind} - {param_name}", value=14, step=1)
            else:
                additional_params[param_name] = st.sidebar.number_input(f"{ind} - {param_name}", value=float(default))
    user_indicator_params[ind] = additional_params

# Compute indicators only if enabled (and if enough data is available)
computed_indicators = {}
for ind in enabled_indicators:
    try:
        result = compute_indicator(ind, price_data, user_indicator_params[ind])
        computed_indicators[ind] = result
    except Exception as e:
        st.warning(f"Could not compute {ind}: {e}")

# Separate indicators automatically into overlays or separate panels based on the indicator's "display" key
overlays = {}
panels = {}
for ind, result in computed_indicators.items():
    display_mode = available_indicators[ind]["display"]
    if isinstance(result, (list, tuple)):
        res_plot = result[0]
    else:
        res_plot = result
    common_length = min(len(close_arr), len(res_plot))
    x_values = price_data["date"][-common_length:]
    y_values = res_plot[-common_length:]
    if display_mode == "overlay":
        overlays[ind] = (x_values, y_values)
    else:
        panels[ind] = (x_values, y_values)


fig = build_stock_chart(date_index=price_data["date"], price=close_arr, overlays=overlays, indicator_panels=panels, strategy_signals=None, ticker=ticker)
st.plotly_chart(fig, use_container_width=True)

