from datetime import datetime, timedelta
import yfinance as yf

import pickle

from libs.utilities import get_last_working_day

file = f'sample/HISTORY_260105_{input("suffix: ")}'

import os

history = None
if(os.path.exists(file)):
    with open(file, 'rb') as f:
        history = pickle.load(f)
else:
    mmdd = input('MMDD ')
    tdate1 = datetime(year=2022,month=int(mmdd[:2]), day=int(mmdd[2:]))
    tdate2 = get_last_working_day(tdate1)
    
    data = yf.download('^NSEBANK', start=tdate2, end=tdate1 + timedelta(days=1), interval='5m')
    history = [{'open':r['Open'], 'close': r['Close'], 'high': r['High'], 'low': r['Low']} for i, r in data.iterrows()]
    with open(file, 'wb') as f:
        pickle.dump(history, f)

while(True):
    if(not history is None):
        print('length', len(history))
        offset = int(input('upto: '))
        if(offset == 0):
            data = history
        else:
            data = history[:offset+1]
        with open('sample/history', 'wb') as f:
            pickle.dump(history, f)
        with open('sample/history_offset', 'wb') as f:
            pickle.dump(data, f)