import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def get_yfinance_data(ticker: str, start_date: datetime, end_date: datetime, interval: str):
    """Retrieve data from Yahoo Finance with handling for API limitations."""
    today = datetime.today()
    tk = yf.Ticker(ticker)

    # Use different cutoff logic based on interval
    if interval == "1m":
        cutoff = today - timedelta(days=30)
        if end_date < cutoff:
            df = tk.history(start=today-timedelta(days=8), end=today, interval=interval)
        elif start_date < cutoff:
            df = tk.history(start=cutoff, end=cutoff+timedelta(days=8), interval=interval)
        else:
            df = tk.history(start=start_date, end=start_date+timedelta(days=8), interval=interval)
    elif interval in ["2m", "5m", "15m", "30m", "90m"]:
        cutoff = today - timedelta(days=60)
        if end_date < cutoff:
            df = tk.history(start=cutoff, end=today, interval=interval)
        elif start_date < cutoff:
            df = tk.history(start=cutoff, end=end_date, interval=interval)
        else:
            df = tk.history(start=start_date, end=end_date, interval=interval)
    elif interval == "1h":
        cutoff = today - timedelta(days=730)
        if end_date < cutoff:
            df = tk.history(start=cutoff, end=today, interval=interval)
        elif start_date < cutoff:
            df = tk.history(start=cutoff, end=end_date, interval=interval)
        else:
            df = tk.history(start=start_date, end=end_date, interval=interval)
    else:
        df = tk.history(start=start_date, end=end_date, interval=interval)
        df.index.name = "Datetime"

    # Ensure proper formatting
    df.reset_index(inplace=False)
    return df.index.to_numpy(), df["Open"].to_numpy(), df["High"].to_numpy(), df["Low"].to_numpy(), df["Close"].to_numpy(), df["Volume"].to_numpy()


def load_csv_data(file_path: str):
    """Load user‐provided CSV data. The CSV must contain columns:
       Date, Open, High, Low, Close, Volume.
    """
    df = pd.read_csv(file_path, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    return df, df.index.to_numpy(), df["Open"].to_numpy(), df["High"].to_numpy(), df["Low"].to_numpy(), df["Close"].to_numpy(), df["Volume"].to_numpy()
