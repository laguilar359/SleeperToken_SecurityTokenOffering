# IMPORTS
import os, websocket, json, pprint, dash, plotly
import pandas as pd
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

from datetime import datetime
from dash.dependencies import Output, Input
from collections import deque
from dotenv import load_dotenv

# VARIABLES
symbol = "SPY"
times = deque(maxlen=500)
times.append(1)
prices = deque(maxlen=500)
prices.append(1)
df = pd.DataFrame()

# ALPACA SOCKET CONNECTION
socket = "wss://data.alpaca.markets/stream"

# LOAD THE .ENV FILE
load_dotenv(verbose=True)

# SET ALPACA API KEYS FROM .ENV FILE
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")


app = dash.Dash(__name__)
app.layout = html.Div([
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=100,
            n_intervals = 0
        )
    ])
###### FUNCTIONS / DICTIONARIES TO SEND / MESSAGES

# OPEN
def on_open(ws):
    print("Opening Connection to Alpaca API Services")

    auth_data = {
        "action": "authenticate",
        "data": {
            "key_id": alpaca_api_key,
            "secret_key": alpaca_secret_key
            }
        }

    ws.send(json.dumps(auth_data))

    channel_data = {
        "action": "listen",
        "data": {
            "streams":[f"Q.{symbol}"]
        }
    }

    ws.send(json.dumps(channel_data))

@app.callback(Output('live-graph','figure'),
        [Input('graph-update','n_intervals')])
def on_message(ws, message):
    print("\n", "="*30, "MESSAGE", "="*30, "\n\n",message,'\n')

    # Turn string into dictionary
    message_data = json.loads(message)

    # Global Variables
    global times
    global prices
    global df

    data = plotly.graph_objs.Scatter(
                x=list(times),
                y=list(prices),
                name='Scatter',
                mode= 'lines+markers'
                )

    # VARIABLES
    if message_data["data"]["ev"] == 'Q':
        
        # VARIABLES FOR QUOTE SCHEMA
        data_symbol = message_data["data"]["T"]
        nano_time = message_data["data"]["t"]
        bid_size = message_data["data"]["s"]
        bid_price = message_data["data"]["p"]
        ask_size = message_data["data"]["S"]
        ask_price = message_data["data"]["P"]

        time = datetime.now()
        times.append(time)
        prices.append(ask_price)
        df = df.append(pd.DataFrame(data={symbol:ask_price}, index=[time]))
        print(ask_price)
    if message_data["data"]["ev"] == 'T':

        # VARIABLES FOR TRADE SCHEMA
        data_symbol = message_data["data"]["T"]
        nano_time = message_data["data"]["t"]
        trade_size = message_data["data"]["s"]
        trade_price = message_data["data"]["p"]

    if message_data["data"]["ev"] == 'AM':

        # VARIABLES FOR MINUTE BAR SCHEMA
        data_symbol = message_data["data"]["T"]
        open_price = message_data["data"]["o"]
        high_price = message_data["data"]["h"]
        low_price = message_data["data"]["l"]
        close_price = message_data["data"]["c"]

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(times),max(times)]),
                                                yaxis=dict(range=[min(prices),max(prices)]),)}
# CLOSE
def on_close(ws):
    print("Closing Connection to Alpaca API Services")



# SOCKET OBJECT INSTANTIATED 
ws = websocket.WebSocketApp(socket, on_open=on_open,
                            on_message=on_message, 
                            on_close=on_close)


# GO GO GO
if __name__ == '__main__':
    ws.run_forever()