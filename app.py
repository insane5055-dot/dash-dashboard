# dash_app.py
import sqlite3
import pandas as pd
from dash import Dash, dcc, html, Output, Input
import plotly.graph_objects as go

DB_PATH = "buy_sell_aggregates.db"

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM aggregates ORDER BY ts_min DESC LIMIT 30", conn)
    conn.close()

    if df.empty:
        return pd.DataFrame()

    df["ts_min"] = pd.to_datetime(df["ts_min"])
    df = df.sort_values("ts_min")
    return df

app = Dash(__name__)
server = app.server   # ← VERY IMPORTANT (Render ke liye)
app.layout = html.Div([
    html.H1("Buy / Sell 1-Min Aggregation Dashboard"),

    dcc.Interval(id="timer", interval=5000, n_intervals=0),

    dcc.Graph(id="bar_graph"),
    dcc.Graph(id="ratio_graph"),

    html.H3("Raw Table"),
    html.Div(id="table")
])

@app.callback(
    Output("bar_graph", "figure"),
    Output("ratio_graph", "figure"),
    Output("table", "children"),
    Input("timer", "n_intervals")
)
def update(n):
    df = load_data()

    if df.empty:
        return go.Figure(), go.Figure(), "No Data Yet..."

    # Bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["ts_min"], y=df["buy_qty"], name="Buy Qty"))
    fig.add_trace(go.Bar(x=df["ts_min"], y=df["sell_qty"], name="Sell Qty"))
    fig.update_layout(barmode="group", title="Buy vs Sell")

    # Ratio graph
    df["ratio"] = df["buy_qty"] / (df["sell_qty"] + 1)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df["ts_min"], y=df["ratio"], mode="lines+markers", name="Buy/Sell Ratio"))
    fig2.update_layout(title="Buy/Sell Ratio")

    # Table output
    table_html = html.Table([
        html.Thead(html.Tr([html.Th(col) for col in df.columns])),
        html.Tbody([
            html.Tr([html.Td(str(df.iloc[i][col])) for col in df.columns])
            for i in range(len(df))
        ])
    ])

    return fig, fig2, table_html

if __name__ == "__main__":
    app.run(debug=True)

