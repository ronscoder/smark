from libs.pubsub import get_ps_1
from libs.tools import mva
from libs.configs import getConfigs
from libs.orderapi import Orderapi
import datetime
from zoneinfo import ZoneInfo
import numpy as np
from scipy.signal import argrelextrema

api = Orderapi()
ps1 = get_ps_1()

#TODO check the condition for every tick, or check with the last candle
def calculate(channel, data):
    # print('history', len(data))
    configs = getConfigs()
    ma_periods = configs['MA_PERIODS']
    order = configs['EXTREMA_ORDER']
    interval = configs['OHLC_MIN']
    extrema_window = configs['EXTREMA_WINDOW']
    closes = [d['close'] for d in data]
    opens = [d['open'] for d in data]
    mashort = mva(min(ma_periods), closes)
    malong = mva(max(ma_periods), closes)
    ltp = closes[-1]
    # ftp = opens[-1]
    timestamp = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))

    direction = None
    ltp_change_pc = (ltp - opens[-2])/opens[-2]*100

    #max min
    Yw = np.fft.rfft(closes)
    Yw[round(order/2):] = 0
    # ys = np.array(closes)
    ys = np.fft.irfft(Yw, len(closes))
    maxids = argrelextrema(ys, np.greater, order=order, mode='clip')[0]
    minids = argrelextrema(ys, np.less, order=order, mode='clip')[0]
    # maxs = [(x, data[x]) for x in maxids]
    # mins = [(x, data[x]) for x in minids]
    extremas = [0]*len(data)
    for maxid in maxids:
        extremas[maxid] = 1
    for minid in minids:
        extremas[minid] = -1
    print('extremas', extremas)
    print('Closes[-2]-[-1]', ltp_change_pc)
    if(abs(ltp_change_pc) > configs['CANDLE_MOMENTUM_PC']):
        if((1 in extremas[-extrema_window:]) and not (-1 in extremas[-extrema_window:]) and (ltp_change_pc < 0)):
            direction = -1
        elif((-1 in extremas[-extrema_window:]) and not (1 in extremas[-extrema_window:]) and (ltp_change_pc > 0)):
            direction = 1
    # if(abs(ltp_change_pc) > configs['CANDLE_MOMENTUM_PC']):
    #     #: Trending
    #     if(ltp > mashort.iloc[-1] > malong.iloc[-1]):
    #         direction = 1
    #     elif(ltp < mashort.iloc[-1] < malong.iloc[-1]):
    #         direction = -1
        
    #     #: Reversal
    #     if(direction == None):
    #         if(mashort.iloc[-1] < malong.iloc[-1]):
    #             cond = ltp > malong.iloc[-1]
    #             if(cond):
    #                 direction = 1
    #         elif(mashort.iloc[-1] > malong.iloc[-1]):
    #             cond = ltp < malong.iloc[-1]
    #             if(cond):
    #                 direction = -1
    print('BANKNIFTY_DIRECTION', direction)
    ps1.publish('BANKNIFTY_DIRECTION', {'timestamp': timestamp, 'direction': direction})


if(__name__=='__main__'):
    print('Scanning direction from history')
    ps1.subscribe(['HISTORY_260105'], calculate)
