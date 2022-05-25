
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

def get_training_data(data):
    configs = getConfigs()
    ma_periods = configs['MA_PERIODS']
    order = configs['EXTREMA_ORDER']
    interval = configs['OHLC_MIN']
    extrema_window = configs['EXTREMA_WINDOW']
    trend_angle = configs['TREND_ANGLE']
    extrema_offset_factor = configs['EXTREMA_OFFSET_FACTOR']
    sd_bdfactor = configs['SD_BDFACTOR']
    sd_calcoffset_factor = configs['SD_CALC_OFFSET_FACTOR']
    closes = [d['close'] for d in data]
    
    params = {}

    freqfact = configs['FREQ_CUTOFF_FACTOR']

    ltp = closes[-1]

    yt = [x - ltp for x in closes]
    lyt = len(yt)
    idx = lyt//(extrema_offset_factor*extrema_window)*(extrema_offset_factor*extrema_window)
    print('idx', idx)
    # extremas, _ = get_extremas(yt[:idx], freqfact, order)
    extremas, _ = get_extremas(yt[:-extrema_offset_factor*extrema_window], freqfact, order)

    maximas_y = [x[1] for i,x in enumerate(extremas) if x[0] == -1]
    maximas_x = [i for i,x in enumerate(extremas) if x[0] == -1]
    minimas_y = [x[1] for i,x in enumerate(extremas) if x[0] == 1]
    minimas_x = [i for i,x in enumerate(extremas) if x[0] == 1]

    res_coeffs = [0,0]
    if(len(maximas_y)>0):
        if(len(maximas_y)>1):
            res_coeffs = np.polyfit(maximas_x, maximas_y, 1)
        else:
            res_coeffs = [0, maximas_y[-1]]
    else:
        res_coeffs = [0, max(yt)]
 
    params['res_coeffs'] = res_coeffs

    sup_coeffs = [0,0]
    if(len(minimas_y)>0):
        if(len(minimas_y)>1):
            sup_coeffs = np.polyfit(minimas_x, minimas_y, 1)
        else:
            sup_coeffs = [0, minimas_y[-1]]
    else:
        sup_coeffs = [0, min(yt)]
 
    params['sup_coeffs'] = sup_coeffs

    std = round(np.std(yt[:((lyt//extrema_window*extrema_window))][-(sd_calcoffset_factor*extrema_window):]))
    params['std'] = std

    x1 = lyt - extrema_offset_factor*extrema_window - 1
    x2 = lyt
    xlist = [x for x in range(x1,x2)]
    price_coeffs = np.polyfit(xlist, yt[x1:x2], 2)
    # print(price_coeffs)
    params['price_coeffs'] = price_coeffs

    return params

def _calculate(data):
    configs = getConfigs()
    ma_periods = configs['MA_PERIODS']
    order = configs['EXTREMA_ORDER']
    interval = configs['OHLC_MIN']
    extrema_window = configs['EXTREMA_WINDOW']
    trend_angle = configs['TREND_ANGLE']
    extrema_offset_factor = configs['EXTREMA_OFFSET_FACTOR']
    sd_bdfactor = configs['SD_BDFACTOR']
    sd_calcoffset_factor = configs['SD_CALC_OFFSET_FACTOR']
    closes = [d['close'] for d in data]
    params = {}
    direction = 0
    freqfact = configs['FREQ_CUTOFF_FACTOR']
    yt = closes
    lyt = len(yt)
    idx = lyt//(extrema_offset_factor*extrema_window)*(extrema_offset_factor*extrema_window)
    print('idx', idx)
    extremas, _ = get_extremas(closes[:idx], freqfact, order)
    # extremas, _ = get_extremas(closes[:idx], freqfact, order)
    params['extremas'] = extremas
    params['yt'] = yt

    maximas_y = [x[1] for i,x in enumerate(extremas) if x[0] == -1]
    maximas_x = [i for i,x in enumerate(extremas) if x[0] == -1]
    minimas_y = [x[1] for i,x in enumerate(extremas) if x[0] == 1]
    minimas_x = [i for i,x in enumerate(extremas) if x[0] == 1]

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
    std = round(np.std(yt[:((lyt//extrema_window*extrema_window))][-(sd_calcoffset_factor*extrema_window):]))
    params['std'] = std
    # prev_closes1 = yt[-(extrema_window*2-1):-(extrema_window-1)]
    prev_closes1 = yt[-extrema_window:-1]
    ltp = yt[-1]              
    if(p_sup is not None):
        sup = round(p_sup(len(yt)-1))
        m2 = p_sup.c[0] if p_sup.order > 0 else 0
        print('m2', m2)
        if(m2 > trend_angle):
            #uptrending
            if(any([sup - std < x < sup + std for x in prev_closes1])):
                if(ltp > sup + sd_bdfactor/2*std):
                    direction = 1
                    print('uptrend, support bounce')
        if(any([sup - (sd_bdfactor+1)*std < x < sup for x in prev_closes1])):
            print('support breaking down')
            direction = 0
            if(ltp < sup - sd_bdfactor*std):
                direction = -1
                print('uptrend, support breakdown')

    if(p_res is not None):
        res = round(p_res(len(yt)-1))
        m1 = p_res.c[0] if p_res.order > 0 else 0
        print('m1', m1)
        if(m2 < -trend_angle):
            #downtrending
            if(any([res - std < x < res + std for x in prev_closes1])):
                if(ltp < res - sd_bdfactor/2*std):
                    direction = -1
                    print('downtrend, resistance bounce')
        if(any([res - (sd_bdfactor+1)*std > x > res for x in prev_closes1])):
            print('resistance breaking down')
            direction = 0
            if(ltp > res - sd_bdfactor*std):
                direction = 1
                print('downtrend, resistance breakdown')

    return direction, params
def _calculate2(data):
    configs = getConfigs()
    ma_periods = configs['MA_PERIODS']
    order = configs['EXTREMA_ORDER']
    interval = configs['OHLC_MIN']
    extrema_window = configs['EXTREMA_WINDOW']
    trend_angle = configs['TREND_ANGLE']
    extrema_offset_factor = configs['EXTREMA_OFFSET_FACTOR']
    sd_bdfactor = configs['SD_BDFACTOR']
    sd_calcoffset_factor = configs['SD_CALC_OFFSET_FACTOR']
    closes = [d['close'] for d in data]
    params = {}
    direction = 0
    freqfact = configs['FREQ_CUTOFF_FACTOR']
    yt = closes
    lyt = len(yt)
    idx = lyt//(extrema_offset_factor*extrema_window)*(extrema_offset_factor*extrema_window)
    print('idx', idx)
    extremas, _ = get_extremas(closes[:idx], freqfact, order)
    # extremas, _ = get_extremas(closes[:idx], freqfact, order)
    params['extremas'] = extremas
    params['yt'] = yt

    maximas_y = [x[1] for i,x in enumerate(extremas) if x[0] == -1]
    maximas_x = [i for i,x in enumerate(extremas) if x[0] == -1]
    minimas_y = [x[1] for i,x in enumerate(extremas) if x[0] == 1]
    minimas_x = [i for i,x in enumerate(extremas) if x[0] == 1]

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
    std = round(np.std(yt[:((lyt//extrema_window*extrema_window))][-(sd_calcoffset_factor*extrema_window):]))
    params['std'] = std
    # prev_closes1 = yt[-(extrema_window*2-1):-(extrema_window-1)]
    prev_closes1 = yt[-extrema_window:-1]
    ltp = yt[-1]              
    if(p_sup is not None):
        sup = round(p_sup(len(yt)-1))
        m2 = p_sup.c[0] if p_sup.order > 0 else 0
        print('m2', m2)
        if(m2 > trend_angle):
            #uptrending
            if(any([sup - std < x < sup + std for x in prev_closes1])):
                if(ltp > sup + sd_bdfactor/2*std):
                    direction = 1
                    print('uptrend, support bounce')
        if(any([sup - (sd_bdfactor+1)*std < x < sup for x in prev_closes1])):
            print('support breaking down')
            direction = 0
            if(ltp < sup - sd_bdfactor*std):
                direction = -1
                print('uptrend, support breakdown')

    if(p_res is not None):
        res = round(p_res(len(yt)-1))
        m1 = p_res.c[0] if p_res.order > 0 else 0
        print('m1', m1)
        if(m2 < -trend_angle):
            #downtrending
            if(any([res - std < x < res + std for x in prev_closes1])):
                if(ltp < res - sd_bdfactor/2*std):
                    direction = -1
                    print('downtrend, resistance bounce')
        if(any([res - (sd_bdfactor+1)*std > x > res for x in prev_closes1])):
            print('resistance breaking down')
            direction = 0
            if(ltp > res - sd_bdfactor*std):
                direction = 1
                print('downtrend, resistance breakdown')

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
