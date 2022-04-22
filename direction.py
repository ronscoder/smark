
import enum
from libs.pubsub import PubSub, get_ps_1
from libs.tools import mva
from libs.configs import getConfigs
import datetime
from zoneinfo import ZoneInfo
import numpy as np
from scipy.signal import argrelextrema



def get_extremas(data, freqcutoff, order=12):
    freqfact = freqcutoff
    closes = data
    if(freqfact == 0.0):
        ys = np.array(closes)
    else:
        Yw = np.fft.rfft(closes)
        print('number of frequencies', len(Yw))
        Yw[round(len(Yw)/freqfact):] = 0
        ys = np.fft.irfft(Yw, len(closes))
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
    # mashort = mva(min(ma_periods), closes)
    # malong = mva(max(ma_periods), closes)
    ltp = closes[-1]
    # ftp = opens[-1]

    direction = None
    ltp_change_pc = (ltp - opens[-extrema_window])/opens[-extrema_window]*100

    #max min
    freqfact = configs['FREQ_CUTOFF_FACTOR']
    extremas, ys = get_extremas(closes, freqfact, order)
    print('Closes[-2]-[-1]', ltp_change_pc)
    print('extrema_window', extrema_window)
    if((-1 in extremas[-extrema_window:]) and not (1 in extremas[-extrema_window:])):
        direction = -1
    elif((1 in extremas[-extrema_window:]) and not (-1 in extremas[-extrema_window:])):
        direction = 1
    return direction, extremas, ys

def calculate(channel, data, ps1: PubSub):    
    if(data is None):
        return
    direction, extremas, ys = _calculate(data)
    print('BANKNIFTY_DIRECTION', direction)
    previous = ps1.get('BANKNIFTY_DIRECTION')
    timestamp = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    ps1.publish('BANKNIFTY_DIRECTION', {'timestamp': timestamp, 'direction': direction, 'extremas': extremas, 'previous':previous})


if(__name__=='__main__'):
    ps1 = get_ps_1('direction')
    print('Scanning direction from history')
    ps1.r.delete('BANKNIFTY_DIRECTION')
    ps1.subscribe(['HISTORY_260105'], lambda channel, data: calculate(channel, data, ps1))
