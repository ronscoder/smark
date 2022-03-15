from libs.configs import getConfig
from libs.pubsub import get_ps_1
import datetime
from libs.utilities import ydownload

p1 = get_ps_1()


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
        now = datetime.datetime.now()
        ltp = tick['last_price']
        if(self.dt == None):
            self.dt = now
            self.high = self.low = self.open = self.close = ltp
        else:
            if(now > self.dt + datetime.timedelta(minutes=self.interval)):
                self.history.append({
                    'open': self.open, 'high': self.high, 'low': self.low, 'close': self.close})
                self.dt = None
                p1.publish(f'HISTORY_{self.token}', self.history)
            else:
                self.high = max([self.high, ltp])
                self.low = min([self.low, ltp])
                self.close = ltp


def is_holiday(date: datetime.date):
    day = date.weekday()
    if(day in [5, 6]):
        return True
    holidays = getConfig('holidays')
    date_string = f'{date.year}{date.month:02}{date.day:02}'
    if(date_string in holidays):
        return True
    return False


def get_last_working_day():
    today = datetime.datetime.today().date()
    lastworkingday = today - datetime.timedelta(days=1)
    while(is_holiday(lastworkingday)):
        lastworkingday = lastworkingday - datetime.timedelta(days=1)
    return lastworkingday


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
                ydata = ydownload(ysymbol, startdate=f'{last_working_day.year}-{last_working_day.month:02}-{last_working_day.day:02}',
                                    enddate=f'{today.year}-{today.month:02}-{today.day+1:02}', interval='5m')
                self.day_histories[token].history = [{'open': ohlc['Open'], 'high': ohlc['High'], 'low': ohlc['Low'],
                                                        'close': ohlc['Close']} for r, ohlc in ydata.iterrows()]

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
