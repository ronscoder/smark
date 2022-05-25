from libs.configs import getConfig
from libs.pubsub import get_ps_1
import datetime
from libs.utilities import ydownload, get_last_working_day
from zoneinfo import ZoneInfo

p1 = get_ps_1('price recorder')


class OHLC:
    def __init__(self, token) -> None:
        self.token = token
        self.dt = None
        self.high = None
        self.low = None
        self.open = None
        self.close = None
        self.history = []
        self.interval = getConfig('OHLC_MIN')

    def feed(self, tick):
        now = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
        ltp = tick['last_price']
        # print('ltp', ltp)
        if(self.dt == None):
            self.dt = now
            self.high = self.low = self.open = self.close = ltp
        else:
            if(now > self.dt + datetime.timedelta(minutes=self.interval) and datetime.time(hour=9, minute=15)<now.time()<datetime.time(hour=3, minute=30)):
                self.history.append({
                    'open': self.open, 'high': self.high, 'low': self.low, 'close': self.close, 'timestamp': self.dt})
                self.dt = None
                print('publishing history', dt)
                p1.publish(f'HISTORY_{self.token}', self.history)
            else:
                self.high = max([self.high, ltp])
                self.low = min([self.low, ltp])
                self.close = ltp


class DayHistories:
    def __init__(self, tokens, ysymbols) -> None:
        self.tokens = tokens
        self.ysymbols = ysymbols
        self.day_histories = {}
        for token in self.tokens:
            self.day_histories[token] = OHLC(token=token)
            if(token in self.ysymbols):
                ysymbol = self.ysymbols[token]
                last_working_day = get_last_working_day(
                )
                today = datetime.datetime.today().date()
                print('downloading historical for ', ysymbol)
                ydata = ydownload(ysymbol, startdate=last_working_day,
                                    enddate=today, interval='5m')
                self.day_histories[token].history = [{'open': ohlc['Open'], 'high': ohlc['High'], 'low': ohlc['Low'],
                                                        'close': ohlc['Close'], 'timestamp': r.to_pydatetime()} for r, ohlc in ydata.iterrows()]
                p1.publish(f'HISTORY_{token}', self.day_histories[token].history)
    def record(self, channel, data):
        # print(channel, data)
        token = data['instrument_token']
        if(token in self.tokens):
            self.day_histories[token].feed(data)


if(__name__ == '__main__'):
    print('running price recorder...')
    tokens = [260105, ]
    ysymbols = {260105: '^NSEBANK'}
    dayhistories = DayHistories(tokens, ysymbols)
    p1.subscribe([f'TICK_{token}' for token in tokens], cb=dayhistories.record)
'''
{'tradable': True, 'mode': 'full', 'instrument_token': 12334338, 'last_price': 103.7, 'last_traded_quantity': 25, 'average_traded_price': 126.94, 'volume_traded': 3153975, 'total_buy_quantity': 87775, 'total_sell_quantity': 93625, 
'ohlc': {'open': 91.0, 'high': 154.1, 'low': 91.0, 'close': 85.3}, 
'change': 21.570926143024625, 'last_trade_time': datetime.datetime(2022, 3, 16, 10, 38, 29), 
'oi': 491050, 'oi_day_high': 491050, 'oi_day_low': 321500, 'exchange_timestamp': datetime.datetime(2022, 3, 16, 10, 38, 29), 


'depth': 
{'buy': [{'quantity': 250, 'price': 103.65, 'orders': 2}, {'quantity': 25, 'price': 103.6, 'orders': 1}, {'quantity': 50, 'price': 103.55, 'orders': 1}, {'quantity': 575, 'price': 103.5, 'orders': 3}, {'quantity': 125, 'price': 103.45, 'orders': 2}], 

'sell': [{'quantity': 25, 'price': 103.95, 'orders': 1}, {'quantity': 225, 'price': 104.0, 'orders': 2}, {'quantity': 25, 'price': 104.05, 'orders': 1}, {'quantity': 625, 'price': 104.1, 'orders': 4}, {'quantity': 400, 'price': 104.15, 'orders': 3}]}}
'''