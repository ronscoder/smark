import pdb
import matplotlib.pyplot as plt
from libs.pubsub import get_ps_1
# import pandas as pd
from libs.candle import plot
from libs.tools import mva
# import pandas as pd
from scipy.signal import argrelextrema
import numpy as np

p1 = get_ps_1()

datap = p1.get('HISTORY_260105')

datap = datap[:-len([x for x in datap if x['close']==x['open']])][:-12]
# import pdb
# pdb.set_trace()

# ax1 = plt.subplot(2, 1, 1)
# ax2 = plt.subplot(2, 1, 2)

data = [{'Open': x['open'], 'Close': x['close'], 'High': x['high'], 'Low': x['low']} for x in datap]
ax1 = plt.gca()
plot(ax1, data)

# mva1 = mva(5, [x['Close'] for x in data])
# mva2 = mva(15, [x['Close'] for x in data])
# ax1.plot(mva1, color='green')
# ax1.plot(mva2, color='red')

# s = pd.Series([x['close'] for x in datap])

# pcs3 = s.rolling(window=3).apply(lambda x: abs((x.iloc[-1]-x.iloc[-3])/x.iloc[-3]*100))
# ax2.plot(pcs3, color='red')

# pcs2 = s.rolling(window=2).apply(lambda x: abs((x.iloc[-1]-x.iloc[-2])/x.iloc[-2]*100))
# ax2.plot(pcs2, color='green')

# plt.show()
ys = np.array([x['Close'] for x in data])
# ys = pd.Series([x['Close'] for x in data])
# while True:
order = 10
# order = int(input('Order: '))
# if(order == 0):
#     break;
maxids = argrelextrema(ys, np.greater, order=order, mode='clip')[0]
minids = argrelextrema(ys, np.less, order=order, mode='clip')[0]
# maxs = [(x, data[x]) for x in maxids]
# mins = [(x, data[x]) for x in minids]
mx = max(ys)
mn = min(ys)
ax1.vlines(maxids, mn, mx, colors='green')
ax1.vlines(minids, mn, mx, colors='red')
    # plt.pause(0.05)
plt.show()
# pdb.set_trace()