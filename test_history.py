import time
from libs.pubsub import get_ps_1
import pickle
import datetime
import os

p1 = get_ps_1()

file = f'temp/HISTORY_260105_{datetime.datetime.now().month}{datetime.datetime.now().day}'
datap = None
if(os.path.exists(file)):
    if(input('Reuse data? ') == 'y'):
        with open(file, 'rb') as f:
            datap = pickle.load(f)
if(datap == None):
    datap = p1.get('HISTORY_260105')
    with open(file, 'wb') as f:
        pickle.dump(datap, f)

ohlcs = datap[:10]
for ohlc in datap[11:]:
    ohlcs.append(ohlc)
    p1.publish(f'HISTORY_260105', ohlcs)
    time.sleep(5)