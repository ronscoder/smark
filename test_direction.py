import os
import pickle
from direction import _calculate

while(True):
    offset = int(input('Enter offset '))
    histohlcs = None
    fpath = 'sample/history'
    if(os.path.exists(fpath)):
        with open(fpath, 'rb') as f:
            histohlcs = pickle.load(f)
    direction = None
    for i in range(len(histohlcs)):
        data = histohlcs[:-(i+1+offset+1)]
        direction, params = _calculate(data)
        if(direction != None):
            print('direction', direction, 'index', len(data)-1)
            input('')


    