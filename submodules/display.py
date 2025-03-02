import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np

def build_stock_chart(date_index, price, overlays: dict, indicator_panels: dict, strategy_signals: dict = None, ticker=""):
    """
    Build an interactive Plotly chart.
    
    Parameters:
      - date_index: numpy array or pandas index for x-axis.
      - price: numpy array for stock prices.
      - overlays: dict of {indicator_name: (x, y)} to overlay on the price chart.
      - indicator_panels: dict of {indicator_name: (x, y)} to display in separate subplots.
      - strategy_signals: dict with keys 'buy' and 'sell', each as (x, y) tuples.
      - ticker: string symbol for title.
    """
    # Determine number of subplots: at least one for price
    n_panels = 1 + len(indicator_panels)
    fig = make_subplots(rows=n_panels, cols=1, shared_xaxes=True,
                        subplot_titles=[f"{ticker} Price"] + list(indicator_panels.keys()))
    
    # Price chart (row 1)
    fig.add_trace(
        go.Scatter(x=date_index, y=price, mode='lines', name='Price', line=dict(color='blue')),
        row=1, col=1
    )
    
    # Overlays on the price chart
    for name, (x, y) in overlays.items():
        fig.add_trace(
            go.Scatter(x=x, y=y, mode='lines', name=name),
            row=1, col=1
        )
    
    # Optionally add strategy signals
    if strategy_signals:
        x_buy, y_buy = strategy_signals.get("buy", ([], []))
        x_sell, y_sell = strategy_signals.get("sell", ([], []))
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
    
    # Add separate indicator panels
    panel_row = 2
    for name, (x, y) in indicator_panels.items():
        fig.add_trace(
            go.Scatter(x=x, y=y, mode='lines', name=name),
            row=panel_row, col=1
        )
        panel_row += 1
    
    fig.update_layout(height=400 * n_panels, title_text=f"{ticker} Analysis", showlegend=True)
    return fig
