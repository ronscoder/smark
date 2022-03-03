import matplotlib.pyplot as plt
from libs.pubsub import get_ps_1
import pandas as pd
p1 = get_ps_1()

datap = p1.get('HISTORY_260105')

ax1 = plt.subplot(2, 1, 1)
ax2 = plt.subplot(2, 1, 2)

closes = [d['close'] for d in datap]
ax1.plot(closes, color='black')

def mva(window_size, data):
    return pd.Series(data).rolling(window=window_size).mean()

ma1 = mva(5, closes)
ax1.plot(ma1, color='green')

ma2 = mva(15, closes)
ax1.plot(ma2, color='red')

diff = [ma2[i]-ma1[i] for i in range(len(closes))]
ax2.plot(diff)

plt.show()
