# IMPORTS
import v20, os, zmq, time
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Dash / Plotly Imports
import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go

# Running 2 functions at once
from multiprocessing import Process
import sys

# ACCOUNT / ACCESS
load_dotenv(verbose=True)
access_token = os.getenv("OANDA_ACCESS_TOKEN")
account_id = os.getenv("OANDA_ACCOUNT_ID")
account_type = os.getenv("OANDA_ACCOUNT_TYPE")

# v20 API / CONTEXT
hostname = 'api-fxpractice.oanda.com'
stream_hostname = 'stream-fxpractice.oanda.com'
stop_stream = False
instrument = "EUR_USD"

global times
times = list()
times.append(1)
global prices
prices = list()
prices.append(1)

ctx_stream = v20.Context(
            hostname=stream_hostname,
            port=443,
            token=access_token,
            stream_timeout=50)

response = ctx_stream.pricing.stream(account_id,
                                     snapshot=True,
                                     instruments=instrument)

app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1000,
            n_intervals = 0
        ),
    ]
)

def stream_data(instrument=instrument, stop=None, ret=False):
        '''
        Starts a real-time data stream.

        Parameters
        ==========
        instrument: string
            valid instrument name
        '''

        stream_instrument = instrument
        ticks = 0
        response = ctx_stream.pricing.stream(
            account_id, snapshot=True,
            instruments=instrument)
        msgs = []
        for msg_type, msg in response.parts():
            msgs.append(msg)
            print(msg_type, msg)
            if msg_type == 'pricing.ClientPrice':

                df = pd.DataFrame()

                ticks += 1
                t = datetime.now()
                bids = msg.bids[0].dict()['price']
                asks = msg.asks[0].dict()['price']

                prices.append(asks)
                times.append(t)
                df = df.append(pd.DataFrame({instrument:float(asks)}, index=[t]))
                df['SMA 20'] = df[instrument].rolling(20).mean()
                df['SMA 50'] = df[instrument].rolling(50).mean()

                if stop is not None:
                    if ticks >= stop:
                        if ret:
                            return msgs
                        break
            if stop_stream:
                if ret:
                    return msgs
                break

@app.callback(Output('live-graph', 'figure'),
        [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):

    data = plotly.graph_objs.Scatter(
                x=list(times),
                y=list(prices),
                name='Scatter',
                mode= 'lines+markers'
                )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(times),max(times)]),
                                                yaxis=dict(range=[min(prices),max(prices)])
                                                )}

#if __name__ == '__main__':
    #app.run_server(debug=True)

if __name__ == "__main__":
    p1 = Process(target=stream_data())
    p1.start()
    p2 = Process(target=app.run_server(debug=True))
    p2.start()

    p1.join()
    p2.join()