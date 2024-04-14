import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
    dcc.Graph(id='live-update-graph'),
    dcc.Graph(id='profit-loss-graph'),
    dcc.Graph(id='trade-outcomes-graph'),
    dcc.Graph(id='kelly-fraction-graph'),
    dcc.Graph(id='sharpe-ratio-graph')
])

# Callback for Kelly Fraction Graph
@app.callback(
    Output('kelly-fraction-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_kelly_fraction_graph(n):
    df = pd.read_csv('trades.csv', parse_dates=['time'])
    fig = px.line(df, x='time', y='kelly_fraction', title='Kelly Fraction Over Time')
    return fig

# Callback for Sharpe Ratio Graph
@app.callback(
    Output('sharpe-ratio-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_sharpe_ratio_graph(n):
    df = pd.read_csv('trades.csv', parse_dates=['time'])
    fig = px.line(df, x='time', y='sharpe_ratio', title='Sharpe Ratio Over Time')
    return fig

# Callback to update the live win rate graph
@app.callback(
    Output('live-update-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_win_rate(n):
    df = pd.read_csv('trades.csv', parse_dates=['time'])
    win_rates = df.groupby(df.time.dt.hour)['profit'].apply(lambda x: (x > 0).mean())
    fig = px.line(x=win_rates.index, y=win_rates, labels={'x': 'Hour of the Day', 'y': 'Win Rate'}, title='Win Rate Over Time by Hour')
    return fig

# Callback to update the profit/loss graph
@app.callback(
    Output('profit-loss-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_profit_loss(n):
    df = pd.read_csv('trades.csv', parse_dates=['time'])
    fig = px.line(df, x='time', y=df['profit'].cumsum(), title='Cumulative Profit and Loss Over Time')
    return fig

# Callback to update the trade outcomes graph
@app.callback(
    Output('trade-outcomes-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_trade_outcomes(n):
    df = pd.read_csv('trades.csv')
    fig = px.histogram(df, x='profit', nbins=20, title='Distribution of Trade Outcomes')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
