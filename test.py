import matplotlib.pyplot as plt
from libs.pubsub import get_ps_1
from price_recorder import get_last_working_day
import datetime
import yfinance as yf

p1 = get_ps_1()

datap = p1.get('HISTORY_260105')

last_working_day = get_last_working_day()
today = datetime.datetime.today().date()
ydata = yf.download('^NSEBANK', start=f'{last_working_day.year}-{last_working_day.month:02}-{last_working_day.day:02}',
                    end=f'{today.year}-{today.month:02}-{today.day+1:02}', interval='5m')

data = [{'open': ohlc['Open'], 'high': ohlc['High'], 'low': ohlc['Low'],
         'close': ohlc['Close']} for r, ohlc in ydata.iterrows()]

import pdb
pdb.set_trace()
# plt.plot([d['close']+50 for d in datap], )
# plt.plot([d['close'] for d in data])
# plt.show()
