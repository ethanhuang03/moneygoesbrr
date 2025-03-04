import streamlit as st
from datetime import datetime, timedelta
from submodules.data_retrieval import get_yfinance_data
from submodules.indicators import compute_indicator, indicator_info, get_valid_indicators
from submodules.display import build_stock_chart
from strategy import SampleStrategy

st.set_page_config(layout="wide", page_title="Stock Market Analysis Platform")
ticker = st.sidebar.text_input("Ticker", "INTC")
start_date = st.sidebar.date_input("Start Date", datetime.today()-timedelta(days=90))
end_date = st.sidebar.date_input("End Date", datetime.today())
interval = st.sidebar.selectbox("Interval", ["1m", "2m", "5m", "15m", "30m", "90m", "1h", "1d", "1mo"])
start_datetime = datetime.combine(start_date, datetime.strptime("09:30", "%H:%M").time())
end_datetime = datetime.combine(end_date, datetime.strptime("16:30", "%H:%M").time())

# Get data from Yahoo Finance
date_index, open_arr, high_arr, low_arr, close_arr, volume_arr = get_yfinance_data(ticker, start_datetime, end_datetime, interval)

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

fig = build_stock_chart(
    date_index=price_data["date"],
    interval=interval,
    price=close_arr,
    computed_indicators=computed_indicators,
    strategy_signals=strategy_signals,
    ticker=ticker
)

st.plotly_chart(fig, use_container_width=True)

