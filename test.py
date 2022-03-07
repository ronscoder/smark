import matplotlib.pyplot as plt
from libs.pubsub import get_ps_1
import pandas as pd
from libs.candle import plot
from libs.tools import mva

p1 = get_ps_1()

datap = p1.get('HISTORY_260105')

data = [{'Open': x['open'], 'Close': x['close'], 'High': x['high'], 'Low': x['low']} for x in datap]
# ax1 = plt.subplot(2, 1, 1)
# ax2 = plt.subplot(2, 1, 2)
ax1 = plt.gca()

plot(ax1, data)

mva1 = mva(5, [x['Close'] for x in data])
mva2 = mva(15, [x['Close'] for x in data])

plt.plot(mva1, color='green')
plt.plot(mva2, color='red')

plt.show()
