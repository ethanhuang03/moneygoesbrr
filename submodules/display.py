import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
from indicators import indicator_info


def build_stock_chart(date_index, interval, price, computed_indicators, strategy_signals=None, ticker=""):
    """
    Build an interactive Plotly chart.

    Parameters:
      - date_index: numpy array or pandas index for the x-axis.
      - price: numpy array for stock prices (typically the close price).
      - computed_indicators: dict of {indicator_name: (list_of_labels, list_of_data_arrays)},
                             where each list_of_labels/list_of_data_arrays has the same length.
      - strategy_signals: dict with keys 'buy' and 'sell', each as (x, y) tuples (optional).
      - ticker: string symbol for the chart title.
    """
    # Prepare structures for plotting
    overlays = {}
    indicator_panels = {}

    # Process computed indicators into overlays and panels
    for ind, (label_list, data_list) in computed_indicators.items():
        display_mode = indicator_info(ind)["Type"]  # e.g. "overlay" or "panel" etc.

        # Loop over each label/array pair
        for sub_label, arr in zip(label_list, data_list):
            # Ensure we only plot up to the minimum length
            common_length = min(len(date_index), len(price), len(arr))
            x_values = date_index[-common_length:]
            y_values = arr[-common_length:]

            if display_mode == "overlay":
                if ind not in overlays:
                    overlays[ind] = []
                overlays[ind].append((x_values, y_values, sub_label))
            else:
                if ind not in indicator_panels:
                    indicator_panels[ind] = []
                indicator_panels[ind].append((x_values, y_values, sub_label))

    # Determine number of subplots (1 for price + 1 per indicator panel)
    n_panels = 1 + len(indicator_panels)
    fig = make_subplots(
        rows=n_panels, cols=1, shared_xaxes=True,
        subplot_titles=[f"{ticker} Price"] + list(indicator_panels.keys())
    )

    # --- Price chart in the first panel ---
    fig.add_trace(
        go.Scatter(x=date_index, y=price, mode='lines', name='Price', line=dict(color='blue')),
        row=1, col=1
    )

    # --- Overlays on top of the price chart ---
    for name, curves in overlays.items():
        for x, y, sub_label in curves:
            fig.add_trace(
                go.Scatter(
                    x=x, y=y, mode='lines',
                    name=f"{name}: {sub_label}"
                ),
                row=1, col=1
            )

    # --- Plot buy/sell signals (if any) ---
    if strategy_signals:
        x_buy, y_buy, x_sell, y_sell = strategy_signals
        fig.add_trace(
            go.Scatter(
                x=x_buy, y=y_buy, mode='markers', name='Buy Signal',
                marker=dict(symbol='triangle-up', color='green', size=10)
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=x_sell, y=y_sell, mode='markers', name='Sell Signal',
                marker=dict(symbol='triangle-down', color='red', size=10)
            ),
            row=1, col=1
        )

    # --- Indicator panels (below the price chart) ---
    panel_row = 2
    for name, curves in indicator_panels.items():
        for x, y, sub_label in curves:
            fig.add_trace(
                go.Scatter(
                    x=x, y=y, mode='lines',
                    name=f"{name}: {sub_label}"
                ),
                row=panel_row, col=1
            )
        panel_row += 1
    '''
    # TODO: Generalise it so it is does the same for different brockerage.
    rangebreaks = [
        dict(bounds=["sat", "mon"]),  # Hide weekends
        dict(bounds=[16.5, 9.5], pattern="hour")  # Hide non-trading hours (16:30 to 9:30)
    ] if interval in ["1m", "2m", "5m", "15m", "30m", "90m", "1h"] else []
    '''
    fig.update_layout(
        height=400 * n_panels,
        title_text=f"{ticker} Analysis",
        showlegend=True#,
        #xaxis=dict(rangebreaks=rangebreaks)  
    )
    fig.update_xaxes(type='category')
    return fig
