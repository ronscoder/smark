
from scipy.signal import argrelextrema
import numpy as np

def get_extremas(data, freqcutoff, order=12):
    freqfact = freqcutoff
    yt = np.array(data)
    # if(freqfact == 0.0):
    #     ys = np.array(closes)
    # else:
    #     Yw = np.fft.rfft(closes)
    #     print('number of frequencies', len(Yw))
    #     Yw[round(len(Yw)/freqfact):] = 0
    #     ys = np.fft.irfft(Yw, len(closes))
    maxids = argrelextrema(yt, np.greater, order=order, mode='clip')[0]
    minids = argrelextrema(yt, np.less, order=order, mode='clip')[0]
    # maxs = [(x, data[x]) for x in maxids]
    # mins = [(x, data[x]) for x in minids]
    extremas = [(0,0)]*len(data)
    for maxid in maxids:
        extremas[maxid] = (-1, yt[maxid])
    for minid in minids:
        extremas[minid] = (1, yt[minid])
    # print('extremas', extremas)
    return extremas, yt