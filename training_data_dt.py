from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import yfinance as yf
from direction import get_training_data
from datetime import datetime
import pandas as pd
import pickle

from libs.utilities import get_last_working_day
from dbmodel import db, TrainingDataModel

db.connect(reuse_if_open=True)


import os

def get_history(yyyymmdd):
    mmdd = yyyymmdd[4:]
    file = f'sample/HISTORY_260105_{mmdd}'
    history = None
    if(os.path.exists(file)):
        with open(file, 'rb') as f:
            history = pickle.load(f)
    else:
        # mmdd = input('MMDD ')
        tdate1 = datetime(year=int(yyyymmdd[:4]),month=int(mmdd[:2]), day=int(mmdd[2:]))
        tdate2 = get_last_working_day(tdate1)
        
        data = yf.download('^NSEBANK', start=tdate2, end=tdate1 + timedelta(days=1), interval='5m')
        history = [{'open':r['Open'], 'close': r['Close'], 'high': r['High'], 'low': r['Low'], 'timestamp':i.to_pydatetime()} for i, r in data.iloc[:-1].iterrows()]
        with open(file, 'wb') as f:
            pickle.dump(history, f)
    return history

def showall():
    for data in TrainingDataModel.select():
        print(data.created_at,data.res_coeffs_0,data.res_coeffs_1,data.sup_coeffs_0,data.sup_coeffs_1,data.price_coeffs_0,data.price_coeffs_1,data.price_coeffs_2,data.long, data.short, data.wait,data.if_trained, data.timestamp),

# a = [{'a':1,'b':2},{'a':3,'b':4}]
# list(filter(lambda x: x['b']==4, a))[0]

if(__name__=='__main__'):
    # history = get_history()
    # import pdb
    # pdb.set_trace()
    edatestr = None
    while(True):
        edatestrin = input('2022MMDD ')
        if(not edatestrin == ''):
            edatestr = edatestrin
        etimestr = input('HHMM ')
        datestr = f'2022{edatestr}'
        history = get_history(datestr)
        if(not history is None):
            # history        
            dt = datetime(year=int(datestr[:4]),month=int(datestr[4:6]), day=int(datestr[6:8]), hour=int(etimestr[:2]), minute=int(etimestr[2:]), tzinfo=ZoneInfo('Asia/Kolkata'))  
            # import pdb;
            # pdb.set_trace()
            sel = list(filter(lambda x: x['timestamp']==dt, history))
            if(len(sel)==0):
                print('cannot find the index')
                continue
            offset = history.index(sel[0])
            if(offset == 0):
                data = history
            else:
                data = history[:offset+1]
            with open('sample/history', 'wb') as f:
                pickle.dump(history, f)
            with open('sample/history_offset', 'wb') as f:
                pickle.dump(data, f)

            dirtext = input('direction: ')
            if(not dirtext == ''):
                direction = int(dirtext)
                if(direction in [1,0,-1]):
                    params = get_training_data(data)
                    print(params)
                    res_coeffs  = params['res_coeffs']
                    sup_coeffs  = params['sup_coeffs']
                    price_coeffs  = params['price_coeffs']
                    # import pdb
                    # pdb.set_trace()
                    td = TrainingDataModel(res_coeffs_0 = res_coeffs[0],
            res_coeffs_1=res_coeffs[1], sup_coeffs_0 = sup_coeffs[0],sup_coeffs_1=sup_coeffs[1], price_coeffs_0 = price_coeffs[0], price_coeffs_1 = price_coeffs[1], price_coeffs_2 = price_coeffs[2], long=1 if direction==1 else 0, short=1 if direction == -1 else 0, wait = 1 if direction ==0 else 0, timestamp=history[offset+1]['timestamp'])
                    try:
                        td.save()
                    except Exception as ex:
                        print('Error', ex.__str__())
            ifloadanother = input('load another y?')
            if(ifloadanother == 'y'):
                history = get_history()


        # for k,v in params.items():
        #     if(k[-1]=='s'):
        #         inputs[len(inputs):] = v
        #     else:
        #         inputs.append(v)
        # output = direction
        #
