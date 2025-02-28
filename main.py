import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt


ticker = "INTC"
start_date = "2017-01-01"
end_date = "2025-02-20"

df = yf.download(ticker, start=start_date, end=end_date)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df = df.reset_index()

df = ta.add_all_ta_features(df, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True)
df['SMA200'] = df['Close'].rolling(window=200).mean()

# -------------------------------------------------------------------
# Define buy and sell conditions:
# Buy when:
#   - MACD crosses above its signal line
#   - RSI < 50
#   - Close > SMA200
#   - ADX >= 25
buy_condition = (
    (df['trend_macd'].shift(1) <= df['trend_macd_signal'].shift(1)) &
    (df['trend_macd_signal'].shift(1) < 0) &
    #(df['momentum_rsi'] < 50) &
    #(df['Close'] > df['SMA200']) &
    (df['trend_adx'] >= 25)
)

# Sell when:
#   - MACD crosses below its signal line
#   - RSI > 50
#   - Close < SMA200
#   - ADX >= 25
sell_condition = (
    (df['trend_macd'].shift(1) >= df['trend_macd_signal'].shift(1)) &
    (df['trend_macd_signal'].shift(1) > 0) &
    #(df['momentum_rsi'] > 50) &
    #(df['Close'] < df['SMA200']) &
    (df['trend_adx'] >= 25)
)
# -------------------------------------------------------------------

fig, axs = plt.subplots(4, 1, figsize=(14, 18), sharex=True)

# 1. Price & 200-day SMA
axs[0].plot(df['Date'], df['Close'], label='Close Price', color='blue')
axs[0].plot(df['Date'], df['SMA200'], label='200-day SMA', color='orange')
axs[0].set_title(f"{ticker} Price & 200-day SMA")
axs[0].set_ylabel("Price")
axs[0].legend()
# Plot buy signals on the price chart
axs[0].scatter(df.loc[buy_condition, 'Date'], df.loc[buy_condition, 'Close'], 
               marker='^', color='green', label='Buy Signal', s=100)
# Plot sell signals on the price chart
axs[0].scatter(df.loc[sell_condition, 'Date'], df.loc[sell_condition, 'Close'], 
               marker='v', color='red', label='Sell Signal', s=100)
axs[0].set_title(f"{ticker} Price & 200-day SMA with Buy/Sell Signals")
axs[0].set_ylabel("Price")
axs[0].legend()

# 2. MACD and MACD Signal + Histogram
axs[1].plot(df['Date'], df['trend_macd'], label='MACD', color='green')
axs[1].plot(df['Date'], df['trend_macd_signal'], label='MACD Signal', color='red')
# Plot the MACD histogram (difference)
axs[1].bar(df['Date'], df['trend_macd_diff'], label='MACD Histogram', color='grey', alpha=0.5)
axs[1].set_title("MACD")
axs[1].set_ylabel("MACD")
axs[1].legend()

# 3. RSI with Overbought/Oversold Levels
axs[2].plot(df['Date'], df['momentum_rsi'], label='RSI', color='purple')
axs[2].axhline(70, color='red', linestyle='--', label='Overbought (70)')
axs[2].axhline(30, color='green', linestyle='--', label='Oversold (30)')
axs[2].set_title("RSI")
axs[2].set_ylabel("RSI")
axs[2].legend()

# 4. ADX with a Trend Threshold
axs[3].plot(df['Date'], df['trend_adx'], label='ADX', color='black')
axs[3].axhline(25, color='blue', linestyle='--', label='Trend Threshold (25)')
axs[3].set_title("ADX")
axs[3].set_ylabel("ADX")
axs[3].set_xlabel("Date")
axs[3].legend()

plt.tight_layout()
plt.show()
