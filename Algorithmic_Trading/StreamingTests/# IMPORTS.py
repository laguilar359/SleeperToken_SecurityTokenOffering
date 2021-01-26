# IMPORTS
import v20, os, zmq, time
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import plotly.graph_objects as go

# ACCOUNT / ACCESS
load_dotenv(verbose=True)
access_token = os.getenv("OANDA_ACCESS_TOKEN")
account_id = os.getenv("OANDA_ACCOUNT_ID")
account_type = os.getenv("OANDA_ACCOUNT_TYPE")

# v20 API / CONTEXT
hostname = 'api-fxpractice.oanda.com'
stream_hostname = 'stream-fxpractice.oanda.com'
stop_stream = False

ctx_stream = v20.Context(
            hostname=stream_hostname,
            port=443,
            token=access_token,
            stream_timeout=50)

response = ctx_stream.pricing.stream(account_id,
                                     snapshot=True,
                                     instruments="EUR_USD")

def stream_data(instrument="EUR_USD", stop=None, ret=False):
        '''
        Starts a real-time data stream.

        Parameters
        ==========
        instrument: string
            valid instrument name
        '''
        
        df = pd.DataFrame()
        times = list()
        prices = list()
        
        stream_instrument = instrument
        ticks = 0
        response = ctx_stream.pricing.stream(
            account_id, snapshot=True,
            instruments="EUR_USD")
        msgs = []
        for msg_type, msg in response.parts():
            msgs.append(msg)
            # print(msg_type, msg)
            if msg_type == 'pricing.ClientPrice':
                
                ticks += 1
                t = datetime.now()
                bids = msg.bids[0].dict()['price']
                asks = msg.asks[0].dict()['price']
                
                prices.append(asks)
                times.append(t)
                df = df.append(pd.DataFrame({instrument:float(asks)}, index=[t]))
                df['SMA 20'] = df[instrument].rolling(20).mean()
                df['SMA 50'] = df[instrument].rolling(50).mean()
                
                fig.data[0].x = df.index
                fig.data[1].x = df.index
                fig.data[2].x = df.index
                fig.data[0].y = df[instrument]
                fig.data[1].y = df['SMA 20']
                fig.data[2].y = df['SMA 50']
                
                if stop is not None:
                    if ticks >= stop:
                        if ret:
                            return msgs
                        break
            if stop_stream:
                if ret:
                    return msgs
                break
                
fig = go.FigureWidget()
fig.add_scatter(name=instrument, line=dict(color='gold'))
fig.add_scatter(name="SMA 20", line=dict(color='firebrick', width=2, dash='dot'), mode='lines+markers')
fig.add_scatter(name="SMA 50", line=dict(color='royalblue', width=2, dash='dot'), mode='lines+markers')
fig