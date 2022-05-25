from datetime import datetime, timedelta
import yfinance as yf
from libs.utilities import ydownload
import pickle
from zoneinfo import ZoneInfo

from libs.utilities import get_last_working_day
from direction import _calculate, get_training_data

file = f'sample/HISTORY_260105_{input("suffix: ")}'

import os

history = None
if(os.path.exists(file)):
    with open(file, 'rb') as f:
        mmdd, history = pickle.load(f)
else:
    mmdd = input('MMDD ')
    tdate1 = datetime(year=2022,month=int(mmdd[:2]), day=int(mmdd[2:]))
    tdate2 = get_last_working_day(tdate1,3)
    print(tdate2, tdate1)
    data = ydownload('^NSEBANK', startdate=tdate2, enddate=tdate1, interval='5m')
    # import pdb
    # pdb.set_trace()
    if(len(data)==0):
        print('no data')
        exit()
    history = [{'open':r['Open'], 'close': r['Close'], 'high': r['High'], 'low': r['Low'], 'timestamp': i.to_pydatetime()} for i, r in data.iterrows()]
    with open(file, 'wb') as f:
        pickle.dump((mmdd, history), f)

if(not history is None):
    # print(history[-1])
    # datestr = input('upto hhmm: ')
    with open('sample/history', 'wb') as f:
        pickle.dump(history, f)

    dt = datetime(year=2022,month=int(mmdd[:2]), day=int(mmdd[2:]), hour=9, minute=30, tzinfo=ZoneInfo('Asia/Kolkata'))  
    offset = [x['timestamp'] for x in history].index(dt)
    for i in range(offset, len(history)):
        data = history[:i]
        direction, params = _calculate(data)
        if(direction!=0):
            with open('sample/history_offset', 'wb') as f:
                pickle.dump(data, f)
            input('continue?')
else:
    print('history is none')