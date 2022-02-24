import yfinance as yf
import datetime
from datetime import timedelta
import pickle
import os
# import matplotlib.pyplot as plt
from libs.pubsub import get_ps_1
import time

tickers = ['^NSEBANK']
today = datetime.datetime.today().date()
oneday = timedelta(days=1)
filename = f'logs/NSEBANK{today.year}{today.month}{today.day}' 
data = None

if(os.path.exists(filename)):
    print('reading', filename)
    with open(filename, 'rb') as f:
        data = pickle.load(f)
else:
    data = yf.download(tickers=tickers, interval='15m', period='2d')
    print('writing', filename)
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def calc_direction():
    pass

if(__name__=='__main__'):
    while True:
        calc_direction()
        time.sleep(10*60)
