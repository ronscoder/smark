from libs.pubsub import get_ps_1
from libs.tools import mva
from libs.configs import getConfig, getConfigs
from libs.orderapi import Orderapi
import datetime
from zoneinfo import ZoneInfo

api = Orderapi()
ps1 = get_ps_1()

#TODO check the condition for every tick, or check with the last candle
def calculate(channel, data):
    # print('history', len(data))
    configs = getConfigs()
    ma_periods = configs['MA_PERIODS']
    closes = [d['close'] for d in data]
    # opens = [d['open'] for d in data]
    mashort = mva(min(ma_periods), closes)
    malong = mva(max(ma_periods), closes)
    ltp = closes[-1]
    # ftp = opens[-1]
    timestamp = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))

    direction = None
    ltp_change_pc = (ltp - closes[-3])/closes[-3]*100

    print('Closes[-3]-[-1]', ltp_change_pc)
    if(abs(ltp_change_pc) > configs['CANDLE_MOMENTUM_PC']):
        #: Trending
        if(mashort.iloc[-1] > malong.iloc[-1]):
            direction = 1
        elif(mashort.iloc[-1] < malong.iloc[-1]):
            direction = -1
        
        #: Reversal
        if(direction == None):
            if(mashort.iloc[-1] < malong.iloc[-1]):
                cond = ltp > closes[-2] and ltp > mashort.iloc[-1]
                if(cond):
                    direction = 1
            elif(mashort.iloc[-1] > malong.iloc[-1]):
                cond = ltp < closes[-2] and ltp < mashort.iloc[-1]
                if(cond):
                    direction = -1
    print('BANKNIFTY_DIRECTION', direction)
    ps1.publish('BANKNIFTY_DIRECTION', {'timestamp': timestamp, 'direction': direction})


if(__name__=='__main__'):
    print('Scanning direction from history')
    ps1.subscribe(['HISTORY_260105'], calculate)
