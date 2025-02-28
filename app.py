import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import plotly.graph_objs as go
from plotly.subplots import make_subplots


st.set_page_config(layout="wide")
# -------------------------
# Sidebar Inputs
# -------------------------
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Ticker", "INTC")
start_date = st.sidebar.date_input("Start Date", date.today()-timedelta(days=10))
end_date = st.sidebar.date_input("End Date", date.today())


# -------------------------
# Download and Prepare Data
# -------------------------
extended_start_date = pd.to_datetime(start_date) - relativedelta(years=10)
df = yf.download(ticker, start=extended_start_date, end=end_date)

if df.empty:
    st.error("No data found for the given ticker and date range.")
else:
    # If DataFrame columns are a MultiIndex, flatten them.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    # Reset index so that Date becomes a column.
    df = df.reset_index()
    
    # Add technical indicators using ta library.
    df = ta.add_all_ta_features(
        df, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True
    )
    # Calculate the 200-day Simple Moving Average.
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    df = df[df['Date'] >= pd.to_datetime(start_date)]

    # -------------------------
    # Define Buy and Sell Conditions
    # -------------------------
    # Buy when:
    # - MACD crosses above its signal line (using prior MACD Signal being negative as extra confirmation)
    # - ADX is at least 25 (indicating a trending environment)
    buy_condition = (
        (df['trend_macd'].shift(1) <= df['trend_macd_signal'].shift(1)) &
        (df['trend_macd_signal'].shift(1) < 0) &
        (df['trend_adx'] >= 25)
    )

    # Sell when:
    # - MACD crosses below its signal line (using prior MACD Signal being positive as extra confirmation)
    # - ADX is at least 25
    sell_condition = (
        (df['trend_macd'].shift(1) >= df['trend_macd_signal'].shift(1)) &
        (df['trend_macd_signal'].shift(1) > 0) &
        (df['trend_adx'] >= 25)
    )

    df['Buy'] = buy_condition.astype(int)
    df['Sell'] = sell_condition.astype(int)

    # -------------------------
    # Create Interactive Plot using Plotly
    # -------------------------
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        subplot_titles=(
            "Price & 200-day SMA with Buy/Sell Signals",
            "MACD (with Signal and Histogram)",
            "RSI (with Overbought/Oversold Levels)",
            "ADX (Trend Strength)"
        ),
        vertical_spacing=0.08
    )

    # 1. Price & SMA with Buy/Sell Signals
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price', line=dict(color='blue')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['SMA200'], mode='lines', name='200-day SMA', line=dict(color='orange')),
        row=1, col=1
    )
    # Mark Buy signals (green up triangles)
    fig.add_trace(
        go.Scatter(
            x=df.loc[buy_condition, 'Date'],
            y=df.loc[buy_condition, 'Close'],
            mode='markers',
            marker=dict(symbol='triangle-up', color='green', size=10),
            name='Buy Signal'
        ),
        row=1, col=1
    )
    # Mark Sell signals (red down triangles)
    fig.add_trace(
        go.Scatter(
            x=df.loc[sell_condition, 'Date'],
            y=df.loc[sell_condition, 'Close'],
            mode='markers',
            marker=dict(symbol='triangle-down', color='red', size=10),
            name='Sell Signal'
        ),
        row=1, col=1
    )

    # 2. MACD, Signal, and Histogram
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['trend_macd'], mode='lines', name='MACD', line=dict(color='green')),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['trend_macd_signal'], mode='lines', name='MACD Signal', line=dict(color='red')),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(x=df['Date'], y=df['trend_macd_diff'], name='MACD Histogram', marker_color='grey', opacity=0.5),
        row=2, col=1
    )

    # 3. RSI with Overbought (70) and Oversold (30) levels
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['momentum_rsi'], mode='lines', name='RSI', line=dict(color='purple')),
        row=3, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    # 4. ADX with Trend Threshold
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['trend_adx'], mode='lines', name='ADX', line=dict(color='black')),
        row=4, col=1
    )
    fig.add_hline(y=25, line_dash="dash", line_color="blue", row=4, col=1)

    fig.update_layout(
        height=1000,
        title_text=f"{ticker} Technical Indicators",
        xaxis_title="Date"
    )

    st.plotly_chart(fig, use_container_width=True)
