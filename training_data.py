from datetime import datetime, timedelta
import yfinance as yf
from direction import get_training_data


import pickle

from libs.utilities import get_last_working_day


from peewee import *
db = SqliteDatabase('./local/training.db')


class TrainingDataModel2(Model):
    created_at = DateTimeField(default=datetime.now)
    res_coeffs_0 = FloatField()
    res_coeffs_1 = FloatField()
    sup_coeffs_0 = FloatField()
    sup_coeffs_1 = FloatField()
    price_coeffs_0 = FloatField()
    price_coeffs_1 = FloatField()
    price_coeffs_2 = FloatField()
    long = IntegerField()
    short = IntegerField()
    wait = IntegerField()
    if_trained = BooleanField(default=False)
    class Meta:
        database = db # This model uses the "training.db" database.

if(db.table_exists(TrainingDataModel2)):
    pass
else:
    db.create_tables([TrainingDataModel2])


db.connect(reuse_if_open=True)


import os

def get_history():
    file = f'sample/HISTORY_260105_{input("suffix: ")}'
    history = None
    if(os.path.exists(file)):
        with open(file, 'rb') as f:
            history = pickle.load(f)
    else:
        mmdd = input('MMDD ')
        tdate1 = datetime(year=2022,month=int(mmdd[:2]), day=int(mmdd[2:]))
        tdate2 = get_last_working_day(tdate1)
        
        data = yf.download('^NSEBANK', start=tdate2, end=tdate1 + timedelta(days=1), interval='5m')
        history = [{'open':r['Open'], 'close': r['Close'], 'high': r['High'], 'low': r['Low']} for i, r in data.iloc[:-1].iterrows()]
        with open(file, 'wb') as f:
            pickle.dump(history, f)
    return history

def showall():
    for data in TrainingDataModel2.select():
        print(data.created_at,data.res_coeffs_0,data.res_coeffs_1,data.sup_coeffs_0,data.sup_coeffs_1,data.price_coeffs_0,data.price_coeffs_1,data.price_coeffs_2,data.long, data.short, data.wait,data.if_trained),

if(__name__=='__main__'):
    history = get_history()
    # import pdb
    # pdb.set_trace()
    while(True):
        if(not history is None):
            print('last index', len(history)-1)
            offset = int(input('upto: '))
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
                    td = TrainingDataModel2(res_coeffs_0 = res_coeffs[0],
            res_coeffs_1=res_coeffs[1], sup_coeffs_0 = sup_coeffs[0],sup_coeffs_1=sup_coeffs[1], price_coeffs_0 = price_coeffs[0], price_coeffs_1 = price_coeffs[1], price_coeffs_2 = price_coeffs[2], long=1 if direction==1 else 0, short=1 if direction == -1 else 0, wait = 1 if direction ==0 else 0)
                    td.save()
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