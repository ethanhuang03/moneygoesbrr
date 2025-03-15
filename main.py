import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta
import numpy as np
from submodules.data_retrieval import get_yfinance_data, get_ibkr_data
from submodules.indicators import compute_indicator, indicator_info, get_valid_indicators
from submodules.display import build_stock_chart
from strategy import SampleStrategy

st.set_page_config(layout="wide", page_title="Stock Market Analysis Platform")

if 'last_signal' not in st.session_state:
    st.session_state['last_signals'] = None

ticker = st.sidebar.text_input("Ticker", "INTC")
end_date = st.sidebar.date_input("End Date", datetime.today())

duration = st.sidebar.selectbox("Duration", ["1 D", "5 D", "1 M", "3 M", "6 M", "1 Y", "2 Y", "5 Y", "10 Y"])
interval = st.sidebar.selectbox("Interval", ["1 min", "2 mins", "5 mins", "15 mins", "30 mins", "1 hour", "1 day", "1 month"])

# Map the user-selected interval to milliseconds for auto-refresh:
interval_mapping = {
    "1 min": 60 * 1000,
    "2 mins": 2 * 60 * 1000,
    "5 mins": 5 * 60 * 1000,
    "15 mins": 15 * 60 * 1000,
    "30 mins": 30 * 60 * 1000,
    "1 hour": 60 * 60 * 1000,
    "1 day": 24 * 60 * 60 * 1000,
    "1 month": 30 * 24 * 60 * 60 * 1000,  # approximate month as 30 days
}
refresh_interval = interval_mapping.get(interval, 60000)
st_autorefresh(interval=refresh_interval, key="chartrefresh")
st.write(f"Page refreshed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

date_index, open_arr, high_arr, low_arr, close_arr, volume_arr = get_ibkr_data(ticker, end_date, duration, interval)

price_data = {
    "date": date_index,
    "open": open_arr,
    "high": high_arr,
    "low": low_arr,
    "close": close_arr,
    "volume": volume_arr
}

st.sidebar.header("Indicator Settings")
enabled_indicators = st.sidebar.multiselect("Choose Indicators", get_valid_indicators())

# Choose Indicators and their Parameters
user_indicator_params = {}
for ind in enabled_indicators:
    st.sidebar.subheader(f"Settings for {ind}")
    info = indicator_info(ind)
    additional_params = {}
    for i, opt in enumerate(info["Options"]):
        additional_params[opt] = st.sidebar.number_input(f"{ind} - {opt}", value=14, step=1)
    user_indicator_params[ind] = additional_params

# Compute Selected Indicators
computed_indicators = {}
for ind in enabled_indicators:
    try:
        computed_indicators[ind] = compute_indicator(ind, price_data, user_indicator_params[ind])
    except Exception as e:
        st.warning(f"Could not compute {ind}: {e}")

# Load Strategy (automatically computes its required indicators if not already loaded)
strategy = SampleStrategy(price_data, computed_indicators, user_indicator_params)
strategy_signals = strategy.generate_signals()
computed_indicators = strategy.computed_indicators

# Check for new signals and notify user
if strategy_signals is not None:
    x_buy, y_buy, x_sell, y_sell = strategy_signals
    # If no previous signals exist, store the current ones
    if st.session_state['last_signals'] is None:
        st.session_state['last_signals'] = {
            'x_buy': x_buy,
            'y_buy': y_buy,
            'x_sell': x_sell,
            'y_sell': y_sell
        }
    else:
        last_signals = st.session_state['last_signals']
        new_buy = False
        new_sell = False

        # Check buy signals: if length differs or content differs, flag as new
        if len(x_buy) != len(last_signals['x_buy']):
            new_buy = True
        else:
            if not np.array_equal(x_buy, last_signals['x_buy']):
                new_buy = True

        # Check sell signals similarly
        if len(x_sell) != len(last_signals['x_sell']):
            new_sell = True
        else:
            if not np.array_equal(x_sell, last_signals['x_sell']):
                new_sell = True

        if new_buy:
            st.write("New BUY signal detected!")
            st.balloons()  # Optional: visual cue
        if new_sell:
            st.write("New SELL signal detected!")
            st.balloons()  # Optional: visual cue

        # Update stored signals with current ones
        st.session_state['last_signals'] = {
            'x_buy': x_buy,
            'y_buy': y_buy,
            'x_sell': x_sell,
            'y_sell': y_sell
        }

fig = build_stock_chart(
    date_index=price_data["date"],
    interval=interval,
    price=close_arr,
    computed_indicators=computed_indicators,
    strategy_signals=strategy_signals,
    ticker=ticker
)

st.plotly_chart(fig, use_container_width=True)

