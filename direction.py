
import enum
from libs.pubsub import PubSub, get_ps_1
from libs.tools import mva
from libs.configs import getConfigs
import datetime
from zoneinfo import ZoneInfo
import numpy as np
from scipy.signal import argrelextrema
import pandas as pd


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

#TODO check the condition for every tick, or check with the last candle

def _calculate(data):
    configs = getConfigs()
    ma_periods = configs['MA_PERIODS']
    order = configs['EXTREMA_ORDER']
    interval = configs['OHLC_MIN']
    extrema_window = configs['EXTREMA_WINDOW']
    trend_angle = configs['TREND_ANGLE']
    closes = [d['close'] for d in data]
    params = {}
    direction = None
    freqfact = configs['FREQ_CUTOFF_FACTOR']
    yt = closes
    lyt = len(yt)
    idx = lyt//extrema_window*extrema_window
    print('idx', idx)
    extremas, _ = get_extremas(closes[:idx], freqfact, order)
    params['extremas'] = extremas
    params['yt'] = yt

    maximas_y = [x[1] for i,x in enumerate(extremas) if x[0] == -1]
    maximas_x = [i for i,x in enumerate(extremas) if x[0] == -1]
    minimas_y = [x[1] for i,x in enumerate(extremas) if x[0] == 1]
    minimas_x = [i for i,x in enumerate(extremas) if x[0] == 1]

    # maximas_y = [x[1] for i,x in enumerate(extremas) if x[0] == -1]
    # maximas_x = [i for i,x in enumerate(extremas) if x[0] == -1]
    # minimas_y = [x[1] for i,x in enumerate(extremas) if x[0] == 1]
    # minimas_x = [i for i,x in enumerate(extremas) if x[0] == 1]

    p_res = None
    if(len(maximas_y)>0):
        if(len(maximas_y)>1):
            p_res = np.poly1d(np.polyfit(maximas_x, maximas_y, 1)) 
        else:
            p_res = np.poly1d([0,maximas_y[0]])
    params['p_res'] = p_res
    p_sup = None
    if(len(minimas_y)>0):
        if(len(minimas_y)>1):
            p_sup = np.poly1d(np.polyfit(minimas_x, minimas_y, 1))
        else:
            p_sup = np.poly1d([0,minimas_y[0]])
    params['p_sup'] = p_sup
    
    # std = round(np.std(yt[-(extrema_window*2):-extrema_window]))
    std = round(np.std(yt[:((lyt//extrema_window*extrema_window))][-extrema_window:]))
    params['std'] = std
    # prev_closes1 = yt[-(extrema_window*2-1):-(extrema_window-1)]
    prev_closes1 = yt[-extrema_window:-1]
    ltp = yt[-1]
    if(p_res is not None):
        res = round(p_res(len(yt)-1))
        m1 = p_res.c[0] if p_res.order > 0 else 0
        print('m1', m1)
        if_around_res = any([res - std < x < res + std for x in prev_closes1])
        # print(res, res-std,prev_closes1,res+std)
        if(if_around_res and m1 < 0):
            if(ltp < res - 2*std):
                direction = -1
                print('resistance bounce')

        if(any([x < (res - 2*std) for x in prev_closes1]) and m1 > 0):
            if(ltp > (res - 2*std)):
                direction = 1
                print('resistance retreat')                
        elif(m1<-5):
            if(any([x < res for x in prev_closes1]) or any([res - std < x < res + std for x in prev_closes1])):
                if(ltp > res + std):
                    direction = 1
                    print('resistance breakdown')                
    if(p_sup is not None):
        sup = round(p_sup(len(yt)-1))
        m2 = p_sup.c[0] if p_sup.order > 0 else 0
        print('m2', m2)
        # if(any([sup - std < x < sup + std for x in prev_closes1])):
        if(any([sup - std < x < sup + std for x in prev_closes1]) and m2 > 0):
            if(ltp > sup + 2*std):
                direction = 1
                print('support bounce')
        if(any([x > (sup + 2*std) for x in prev_closes1]) and m2 < 0):
            if(ltp < (sup + 2*std)):
                direction = -1
                print('support retreat')
        elif(m2>5):
            if(any([x > sup for x in prev_closes1]) or any([sup - std < x < sup + std for x in prev_closes1])):
                if(ltp < sup - std):
                    direction = -1
                    print('support breakdown')

    # breakouts
    if(not None in (p_sup, p_res)):
        m1 = p_res.c[0] if p_res.order > 0 else 0
        m2 = p_sup.c[0] if p_sup.order > 0 else 0

        m12 = m1 - m2
        res = round(p_res(len(yt)-1))
        sup = round(p_sup(len(yt)-1))
        print('m1-m2',m12)
        if(m12 < -trend_angle):
            # merging
            # res breakout
            if(any([res - std < x < res + std for x in prev_closes1])):
                if(ltp > res + std):
                    direction = 1
                    print('resistance breakout')
            # sup breakout
            if(any([sup - std < x < sup + std for x in prev_closes1])):
                if(ltp < sup - std):
                    direction = -1
                    print('support breakout')
        


    return direction, params

def calculate(channel, data, ps1: PubSub):    
    if(data is None):
        return
    direction, params = _calculate(data)

    timestamp = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    ps1.publish('BANKNIFTY_DIRECTION', {'timestamp': timestamp, 'direction': direction, 'params': params})


if(__name__=='__main__'):
    ps1 = get_ps_1('direction')
    print('Scanning direction from history')
    ps1.r.delete('BANKNIFTY_DIRECTION')
    ps1.subscribe(['HISTORY_260105'], lambda channel, data: calculate(channel, data, ps1))
