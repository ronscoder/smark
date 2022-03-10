import matplotlib.pyplot as plt
from libs.pubsub import get_ps_1
import pandas as pd
from libs.candle import plot
from libs.tools import mva
import pandas as pd

p1 = get_ps_1()

datap = p1.get('HISTORY_260105')

ax1 = plt.subplot(2, 1, 1)
ax2 = plt.subplot(2, 1, 2)

data = [{'Open': x['open'], 'Close': x['close'], 'High': x['high'], 'Low': x['low']} for x in datap]
# ax1 = plt.gca()
plot(ax1, data)

mva1 = mva(5, [x['Close'] for x in data])
mva2 = mva(15, [x['Close'] for x in data])
ax1.plot(mva1, color='green')
ax1.plot(mva2, color='red')

s = pd.Series([x['close'] for x in datap])

pcs3 = s.rolling(window=3).apply(lambda x: abs((x.iloc[-1]-x.iloc[-3])/x.iloc[-3]*100))
ax2.plot(pcs3, color='red')

pcs2 = s.rolling(window=2).apply(lambda x: abs((x.iloc[-1]-x.iloc[-2])/x.iloc[-2]*100))
ax2.plot(pcs2, color='green')

plt.show()
