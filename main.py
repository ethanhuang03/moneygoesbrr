import yfinance as yf
from datetime import datetime, timedelta
import tulipy as ti
import pytz

import streamlit as st
import plotly.graph_objs as go
from plotly.subplots import make_subplots


TICKER = "INTC"
START_DATE = datetime.strptime("2017-02-01", "%Y-%m-%d")
END_DATE = datetime.strptime("2025-02-28", "%Y-%m-%d")


def get_data(ticker, start_date, end_date, interval):
    today = datetime.today()
    tk = yf.Ticker(ticker)

    if interval == "1m":
        # If the end date is more than 30 days ago, get most recent (8 day) data. 
        # If the start date is more than 30 days ago, get data from cutoff to 8 days (API limit)
        # If the start date is within the last 30 days, get data from start date to 8 days (API limit)
        cutoff = today - timedelta(days=30)
        if end_date < cutoff:
            df = tk.history(start=today-timedelta(days=8), end=today, interval=interval)
        elif start_date < cutoff:  
            df = tk.history(start=cutoff, end=cutoff+timedelta(days=8), interval=interval)
        else:  
            df = tk.history(start=start_date, end=start_date+timedelta(days=8), interval=interval)
            # df = tk.history(start=end_date-timedelta(days=8), end=end_date, interval=interval, period="max")
    elif interval in ["2m", "5m", "15m", "30m", "90m"]:
        # If the end date is more than 60 days ago, get most recent (60 day) data
        # If the start date is more than 60 days ago, get data from cutoff to end date
        # If the start date is within the last 60 days, get data from start date to end date
        cutoff = today - timedelta(days=60)
        if end_date < cutoff:  
            df = tk.history(start=cutoff, end=today, interval=interval)
        elif start_date < cutoff:  
            df = tk.history(start=cutoff, end=end_date, interval=interval)
        else:  
            df = tk.history(start=start_date, end=end_date, interval=interval)
    elif interval == "1h":
        # If the end date is more than 2 years ago, get most recent (2 year) data
        # If the start date is more than 2 years ago, get data from cutoff to end date
        cutoff = today - timedelta(days=730)
        if end_date < cutoff:  
            df = tk.history(start=cutoff, end=today, interval=interval)
        elif start_date < cutoff:  
            df = tk.history(start=cutoff, end=end_date, interval=interval)
        else:  # If the start date is within the last 2 years, get data from start date to end date
            df = tk.history(start=start_date, end=end_date, interval=interval)
    else:
        df = tk.history(start=start_date, end=end_date, interval=interval)
        df.index.name = "Datetime"

    return df, df["Open"].to_numpy(), df["High"].to_numpy(), df["Low"].to_numpy(), df["Close"].to_numpy(), df["Volume"].to_numpy()


def print_info(indicator):
    print("Type:", indicator.type)
    print("Full Name:", indicator.full_name)
    print("Inputs:", indicator.inputs)
    print("Options:", indicator.options)
    print("Outputs:", indicator.outputs)


st.set_page_config(layout="wide")

st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Ticker", "INTC")
start_date = datetime.combine(
    st.sidebar.date_input("Start Date", datetime.today()-timedelta(days=10)), 
    datetime.strptime("09:30", "%H:%M").time())
end_date = datetime.combine(
    st.sidebar.date_input("End Date", datetime.today()), 
    datetime.strptime("16:30", "%H:%M").time())
interval = st.sidebar.selectbox("Interval", ["1m", "2m", "5m", "15m", "30m", "90m", "1h", "1d", "1mo"])


# Indicator Calculations:
df, o, h, l, c, v = get_data(ticker, start_date, end_date, interval)
print(df)
macd, macd_signal, macd_hist = ti.macd(c, 12, 26, 9)
dx = ti.adx(h, l, c, 14)
ema = ti.ema(c, 200)
rsi = rsi = ti.rsi(c, 14)

# Align the indicator arrays with the DataFrame index
ema_index = df.index[-len(ema):]
macd_index = df.index[-len(macd):]
dx_index = df.index[-len(dx):]
rsi_index = df.index[-len(rsi):]

# Find the common length of all arrays
common_length = min(len(ema), len(macd), len(macd_signal), len(dx))
common_index = df.index[-common_length:]
c_common = c[-common_length:]
ema_common = ema[-common_length:]
macd_common = macd[-common_length:]
macd_signal_common = macd_signal[-common_length:]
dx_common = dx[-common_length:]


# Strategy
# Buy when:
#   - MACD crosses above its signal line and MACD Signal is negative
#   - ADX is at least 25
#   - Close > 200-day EMA
# Sell when:
#   - MACD crosses below its signal line and MACD Signal is positive
#   - ADX is at least 25
#   - Close < 200-day EMA
# Define Buy/Sell Conditions based on the strategy:
buy_condition = (
    (macd_common <= macd_signal_common) &
    (macd_signal_common < 0) &
    (dx_common >= 25) #&
    #(c[-min_length:] < ema[-min_length:])
)
sell_condition = (
    (macd_common >= macd_signal_common) &
    (macd_signal_common > 0) &
    (dx_common >= 25) #&
    #(c[-min_length:] > ema[-min_length:])
)
x_buy = common_index[buy_condition]
y_buy = c_common[buy_condition]
x_sell = common_index[sell_condition]
y_sell = c_common[sell_condition]


fig = make_subplots(
    rows=4, cols=1, shared_xaxes=True,
    subplot_titles=[
        f"{TICKER} Price & 200-day EMA",
        "MACD", "ADX", "RSI"
    ]
)

# 1. Price & 200-day EMA & Buy/Sell Signals
fig.add_trace(
    go.Scatter(x=df.index, y=c, mode='lines', name='Close Price', line=dict(color='blue')),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=ema_index, y=ema, mode='lines', name='200-day EMA', line=dict(color='orange')),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=x_buy, y=y_buy, mode='markers', name='Buy Signal',
               marker=dict(symbol='triangle-up', color='green', size=10)),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=x_sell, y=y_sell, mode='markers', name='Sell Signal',
               marker=dict(symbol='triangle-down', color='red', size=10)),
    row=1, col=1
)

# 2. MACD, MACD Signal, and Histogram
fig.add_trace(
    go.Scatter(x=macd_index, y=macd, mode='lines', name='MACD', line=dict(color='green')),
    row=2, col=1
)
fig.add_trace(
    go.Scatter(x=macd_index, y=macd_signal, mode='lines', name='MACD Signal', line=dict(color='red')),
    row=2, col=1
)
fig.add_trace(
    go.Bar(x=macd_index, y=macd_hist, name='MACD Histogram', marker_color='grey', opacity=0.5),
    row=2, col=1
)

# 3. ADX with Trend Threshold
fig.add_trace(
    go.Scatter(x=dx_index, y=dx, mode='lines', name='ADX', line=dict(color='black')),
    row=3, col=1
)
fig.add_trace(
    go.Scatter(x=dx_index, y=[25]*len(dx_index), mode='lines', name='Trend Threshold (25)',
               line=dict(dash='dash', color='blue')),
    row=3, col=1
)

# 4. RSI with Overbought/Oversold Levels
fig.add_trace(
    go.Scatter(x=rsi_index, y=rsi, mode='lines', name='RSI', line=dict(color='purple')),
    row=4, col=1
)
fig.add_trace(
    go.Scatter(x=rsi_index, y=[70]*len(rsi_index), mode='lines', name='Overbought (70)',
               line=dict(dash='dash', color='red')),
    row=4, col=1
)
fig.add_trace(
    go.Scatter(x=rsi_index, y=[30]*len(rsi_index), mode='lines', name='Oversold (30)',
               line=dict(dash='dash', color='green')),
    row=4, col=1
)

fig.update_layout(
    height=900,
    width=1000,
    title_text=f"{TICKER} Analysis with Full Data for Price & Indicators",
    showlegend=True
)

# Display the Plotly figure in Streamlit
st.plotly_chart(fig)