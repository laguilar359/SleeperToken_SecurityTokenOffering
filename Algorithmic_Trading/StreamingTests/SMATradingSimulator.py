# Connecting to TickerSimulator
import zmq

# Getting floating numbers through RegEx
import re

# Data Visualization - etc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from datetime import datetime
import plotly.graph_objects as go

# Running 2 functions at once
import _thread

# Connection Established / Subscribed
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:5555")
socket.setsockopt_string(zmq.SUBSCRIBE, '')

msgs = list()
msgs.append(1)
prices = list()
prices.append(1)
times = list()
times.append(1)
df = pd.DataFrame()

fig = go.FigureWidget()

def stream_data(stop=None, ret=False):

    ticks = 0
    global df
    global prices
    global times

    while True:

        # String based messages is received
        msg = socket.recv_string()

        price = float(re.findall("\d+\.\d+", msg)[0])
        t = datetime.now()
        times.append(t)
        prices.append(price)
        df = df.append(pd.DataFrame(data={'Price':price}, index=[t]))
        df['SMA1'] = df['Price'].rolling(5).mean()
        df['SMA2'] = df['Price'].rolling(10).mean()
        df['Return'] = np.log(df['Price'] / df['Price'].shift(1))
        df['Position'] = np.where(df['SMA1'] > df['SMA2'], 1, -1)
        df['Signal'] = df['Position'][df['Position'].diff() != 0]
        df['Signal'].fillna(0, inplace=True)

        print(df.tail(1))

        fig.data[0].x = df.index
        fig.data[1].x = df.index
        fig.data[2].x = df.index
        fig.data[0].y = df["Price"]
        fig.data[1].y = df['SMA1']
        fig.data[2].y = df['SMA2']
        fig.show()


fig.add_scatter(name="Price", line=dict(color='gold'))
fig.add_scatter(name="SMA1", line=dict(color='firebrick', width=2, dash='dot'), mode='lines+markers')
fig.add_scatter(name="SMA2", line=dict(color='royalblue', width=2, dash='dot'), mode='lines+markers')

if __name__ == "__main__":
    stream_data()
