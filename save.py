import time
from libs.pubsub import get_ps_1
import pickle
import datetime
import os

p1 = get_ps_1()

file = f'temp/HISTORY_260105_{input("suffix: ")}'
datap = p1.get('HISTORY_260105')
with open(file, 'wb') as f:
    pickle.dump(datap, f)