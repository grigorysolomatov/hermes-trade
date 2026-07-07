import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import pandas as pd
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Hermes Trade v0.1"

SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "NVDA", "BTC-USD", "ETH-USD", "EUR-USD=X", "GC=F"
]

PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y"]

INTERVALS = ["1m", "5m", "15m", "30m", "1h", "1d"]

app.layout = dbc.Container([
    dcc.Interval(
        id='interval-component',
        interval=60*1000,
        n_intervals=0
    ),

    dbc.Row([
        dbc.Col([
            html.H1("Hermes Trade v0.1", className="text-center mb-3 mt-3"),
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Symbol", className="fw-bold"),
            dcc.Dropdown(
                id='symbol-dropdown',
                options=[{'label': sym, 'value': sym} for sym in SYMBOLS],
                value='AAPL',
                clearable=False,
                style={'color': '#000'}
            )
        ], width=4),

        dbc.Col([
            html.Label("Period", className="fw-bold"),
            dcc.Dropdown(
                id='period-dropdown',
                options=[{'label': p, 'value': p} for p in PERIODS],
                value='1d',
                clearable=False,
                style={'color': '#000'}
            )
        ], width=4),

        dbc.Col([
            html.Label("Interval", className="fw-bold"),
            dcc.Dropdown(
                id='interval-dropdown',
                options=[{'label': i, 'value': i} for i in INTERVALS],
                value='5m',
                clearable=False,
                style={'color': '#000'}
            )
        ], width=4),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id='current-price', className="text-center"),
                    html.P(id='price-change', className="text-center mb-0"),
                    html.P(id='last-updated', className="text-center text-muted small mb-0")
                ])
            ], className="mb-4")
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='price-chart', config={'displayModeBar': True})
        ], width=12)
    ])

], fluid=True)

def fetch_data(symbol, period, interval):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)

        if df.empty:
            return None, None, None, None, None

        # Flatten MultiIndex columns for yfinance 1.5.1+
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Reset index to make datetime a column for Plotly
        df = df.reset_index()

        # Rename the datetime column to "Datetime" for consistency
        if 'Date' in df.columns:
            df.rename(columns={'Date': 'Datetime'}, inplace=True)
        elif 'Datetime' not in df.columns and len(df.columns) > 0:
            # The first column should be the datetime index
            df.rename(columns={df.columns[0]: 'Datetime'}, inplace=True)

        # Set Datetime as index for compatibility with existing chart code
        if 'Datetime' in df.columns:
            df.set_index('Datetime', inplace=True)

        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[0]
        price_change = current_price - prev_price
        pct_change = (price_change / prev_price) * 100
        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return df, current_price, pct_change, last_update, symbol
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None, None, None, None

def create_chart(df, symbol):
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="#888")
        )
        fig.update_layout(
            template="plotly_dark",
            height=600,
            paper_bgcolor='#060606',
            plot_bgcolor='#060606'
        )
        return fig

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{symbol} Price', 'Volume')
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC',
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444'
        ),
        row=1, col=1
    )

    colors = ['#00ff88' if row['Close'] >= row['Open'] else '#ff4444'
              for _, row in df.iterrows()]

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )

    fig.update_layout(
        template="plotly_dark",
        height=600,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        paper_bgcolor='#060606',
        plot_bgcolor='#060606',
        font=dict(color='#fff'),
        margin=dict(l=50, r=50, t=50, b=50)
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#222')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#222')

    return fig

@app.callback(
    [Output('price-chart', 'figure'),
     Output('current-price', 'children'),
     Output('price-change', 'children'),
     Output('last-updated', 'children')],
    [Input('symbol-dropdown', 'value'),
     Input('period-dropdown', 'value'),
     Input('interval-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_dashboard(symbol, period, interval, n):
    df, current_price, pct_change, last_update, sym = fetch_data(symbol, period, interval)

    fig = create_chart(df, symbol)

    if current_price is None:
        return fig, "N/A", "No data available", ""

    price_text = f"${current_price:,.2f}"

    change_color = "text-success" if pct_change >= 0 else "text-danger"
    change_symbol = "+" if pct_change >= 0 else ""
    change_text = html.Span(
        f"{change_symbol}{pct_change:.2f}%",
        className=f"{change_color} fw-bold"
    )

    update_text = f"Last updated: {last_update}"

    return fig, price_text, change_text, update_text

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050, debug=False)
