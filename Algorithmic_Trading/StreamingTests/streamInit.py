# IMPORTS
import os, websocket, json, pprint, dash, plotly
import pandas as pd
import numpy as np

from datetime import datetime
from collections import deque
from dotenv import load_dotenv

# ALPACA SOCKET CONNECTION
socket = "wss://data.alpaca.markets/stream"

# LOAD THE .ENV FILE
load_dotenv(verbose=True)

# SET ALPACA API KEYS FROM .ENV FILE
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")