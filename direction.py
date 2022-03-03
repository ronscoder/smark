from libs.pubsub import get_ps_1
from libs.tools import mva
from libs.configs import getConfig
from libs.orderapi import Orderapi
import datetime
from zoneinfo import ZoneInfo

api = Orderapi()
ps1 = get_ps_1()


def calculate(channel, data):
    # print('history', len(data))
    ma_periods = getConfig('MA_PERIODS')
    closes = [d['close'] for d in data]
    mashort = mva(min(ma_periods), closes)
    malong = mva(max(ma_periods), closes)
    ltp = ps1.get('TICK_260105')['last_price']
    timestamp = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    if(ltp < mashort[-1] < malong[-1]):
        print('BANKNIFTY_DIRECTION', 1)
        ps1.set('BANKNIFTY_DIRECTION', {'timestamp': timestamp, 'direction': 1})
    elif(ltp > mashort[-1] > malong[-1]):
        print('BANKNIFTY_DIRECTION', -1)
        ps1.set('BANKNIFTY_DIRECTION', {'timestamp': timestamp, 'direction': -1})
    else:
        print('BANKNIFTY_DIRECTION', 0)
        ps1.set('BANKNIFTY_DIRECTION', None)


if(__name__=='__main__'):
    print('Scanning direction from history')
    ps1.subscribe(['HISTORY_260105'], calculate)