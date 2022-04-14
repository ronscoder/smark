from libs.pubsub import get_ps_1
ps1 = get_ps_1()

import pickle

file = f'temp/HISTORY_260105_{input("suffix: ")}'
data = None
with open(file, 'rb') as f:
    data = pickle.load(f)

from direction import calculate

while(True):
    if(not data is None):
        offset = int(input('upto: '))
        ps1.publish('HISTORY_260105', data[:offset+1])
        calculate('', data[:offset+1])