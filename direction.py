
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
    ys = np.array(data)
    # if(freqfact == 0.0):
    #     ys = np.array(closes)
    # else:
    #     Yw = np.fft.rfft(closes)
    #     print('number of frequencies', len(Yw))
    #     Yw[round(len(Yw)/freqfact):] = 0
    #     ys = np.fft.irfft(Yw, len(closes))
    maxids = argrelextrema(ys, np.greater, order=order, mode='clip')[0]
    minids = argrelextrema(ys, np.less, order=order, mode='clip')[0]
    # maxs = [(x, data[x]) for x in maxids]
    # mins = [(x, data[x]) for x in minids]
    extremas = [0]*len(data)
    for maxid in maxids:
        extremas[maxid] = -1
    for minid in minids:
        extremas[minid] = 1
    print('extremas', extremas)
    return extremas, ys

#TODO check the condition for every tick, or check with the last candle

def _calculate(data):
    # print('history', len(data))
    configs = getConfigs()
    ma_periods = configs['MA_PERIODS']
    order = configs['EXTREMA_ORDER']
    interval = configs['OHLC_MIN']
    extrema_window = configs['EXTREMA_WINDOW']
    closes = [d['close'] for d in data]
    opens = [d['open'] for d in data]

    conditions = {}
    # mashort = mva(min(ma_periods), closes)
    # malong = mva(max(ma_periods), closes)
    # ltp = closes[-1]
    # ftp = opens[-1]

    direction = None
    ltp_change_pc = (closes[-1] - opens[-1])/opens[-1]*100
    print('ltp_change_pc', ltp_change_pc)
    #max min
    freqfact = configs['FREQ_CUTOFF_FACTOR']
    # ys = mva(4, closes)
    extremas, ys = get_extremas(closes, freqfact, order)
    extremas_values = [(extremas[i],ys[i]) for i in range(len(extremas)) if extremas[i]!=0]
    # print('extrema_window', extrema_window)
    # import pdb
    # pdb.set_trace()
    if_good_extrema_gap = True
    if(len(extremas_values[-2:])>1):
        if(extremas_values[-1][0] != extremas_values[-2][0]):
            gap = abs(extremas_values[-1][1] - extremas_values[-2][1])
            print('extrema gap', gap)
            if(not gap > configs['EXTREMA_GAP']):
                if_good_extrema_gap = False
    if((-1 in extremas[-extrema_window:]) and not (1 in extremas[-extrema_window:])):
        direction = -1
    elif((1 in extremas[-extrema_window:]) and not (-1 in extremas[-extrema_window:])):
        direction = 1
    
    # if price breaks all resistance
    if_resistance_broken = False
    raovs = [x for d, x in extremas_values if d==-1][-2:]
    # print('raovs', raovs, 'closes[-1]', closes[-1])
    if(all([ close > aov for close in closes[-2:] for aov in raovs])):
        print('resistance broken - apparent')
        if(any([close < aov for close in closes[-4:-2] for aov in raovs])):
            print('resistance broken confirmed')
            if_resistance_broken = True
            direction = 1
    print('if_resistance_broken', if_resistance_broken)        

    # if price breaks all supports
    if_support_broken = False
    saovs = [x for d, x in extremas_values if d==1][-2:]
    # print('raovs', raovs, 'closes[-1]', closes[-1])
    if(all([ close < aov for close in closes[-2:] for aov in saovs])):
        if(any([close > aov for close in closes[-4:-2] for aov in saovs])):
            if_support_broken = True
            direction = -1
    print('if_support_broken', if_support_broken)        

    return direction, extremas, ys, if_good_extrema_gap, abs(ltp_change_pc) > configs['CANDLE_MOMENTUM_PC'], if_resistance_broken, if_support_broken

def calculate(channel, data, ps1: PubSub):    
    if(data is None):
        return
    direction, extremas, ys, if_good_gap, if_good_momentum, if_resistance_broken, if_support_broken = _calculate(data)
    print('BANKNIFTY_DIRECTION', direction, 'if_good_gap', if_good_gap)
    previous = ps1.get('BANKNIFTY_DIRECTION')
    timestamp = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    ps1.publish('BANKNIFTY_DIRECTION', {'timestamp': timestamp, 'direction': direction, 'extremas': extremas, 'previous':previous, 'if_good_gap': if_good_gap, 'if_good_momentum': if_good_momentum, 'if_resistance_broken':if_resistance_broken, 'if_support_broken':if_support_broken})


if(__name__=='__main__'):
    ps1 = get_ps_1('direction')
    print('Scanning direction from history')
    ps1.r.delete('BANKNIFTY_DIRECTION')
    ps1.subscribe(['HISTORY_260105'], lambda channel, data: calculate(channel, data, ps1))
