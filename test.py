import pdb
import matplotlib.pyplot as plt
from libs.pubsub import get_ps_1
# import pandas as pd
from libs.candle import plot
from libs.tools import mva
# import pandas as pd
from scipy.signal import argrelextrema
import numpy as np
import pickle
import datetime
import os

p1 = get_ps_1()

file = f'temp/HISTORY_260105_{datetime.datetime.now().month}{datetime.datetime.now().day}'
if(os.path.exists(file)):
    with open(file, 'rb') as f:
        datap = pickle.load(f)
else:
    datap = p1.get('HISTORY_260105')
    with open(file, 'wb') as f:
        pickle.dump(datap, f)

# datap = datap[:-len([x for x in datap if x['close']==x['open']])][:-12]
# import pdb
# pdb.set_trace()

# ax1 = plt.subplot(2, 1, 1)
# ax2 = plt.subplot(2, 1, 2)

datax = [{'Open': x['open'], 'Close': x['close'], 'High': x['high'], 'Low': x['low']} for x in datap]
ax1 = plt.gca()
# ax1.set_xscale()
x_ticks = list(range(len(datax)))
# plt.xticks(x_ticks, x_ticks)
# plt.set_xlim([0, len(datax)])
# plt.xlim([0, len(datax)])
data = []
# plt.ion()
mx = max([x['Close'] for x in datax])
mn = min([x['Close'] for x in datax])
# for row in datax:
#     data.append(row)
#     plot(ax1, data)
#     # ys = np.array([x['Close'] for x in data])
#     # opens = [x['Open'] for x in data]
#     closes = [x['Close'] for x in data]
#     # ys = np.array([])
#     # yss = []
#     # for i in range(len(data)):
#     #     yss.append(opens[i])
#     #     yss.append(closes[i])
#     # ys = np.array(closes)
#     Yw = np.fft.rfft(closes)
#     Yw[round(len(Yw)/3):] = 0
#     ys = np.fft.irfft(Yw, len(closes))
#     # ys = pd.Series([x['Close'] for x in data])
#     # while True:
#     order = 18
#     # order = int(input('Order: '))
#     # if(order == 0):
#     #     break;
#     # ax1.plot(ys, color='yellow')
#     maxids = argrelextrema(ys, np.greater, order=order, mode='clip')[0]
#     minids = argrelextrema(ys, np.less, order=order, mode='clip')[0]
#     # maxs = [(x, data[x]) for x in maxids]
#     # mins = [(x, data[x]) for x in minids]
#     ax1.vlines(maxids, mn, mx, colors='green')
#     ax1.vlines(minids, mn, mx, colors='red')
#         # plt.pause(0.05)
#     extremas = [0]*len(data)
#     for maxid in maxids:
#         extremas[round(maxid)] = 1
#     for minid in minids:
#         extremas[round(minid)] = -1
#     print(extremas)
#     direction = None
#     if((1 in extremas[-3:]) and not (-1 in extremas[-3:])):
#         direction = -1
#     elif((-1 in extremas[-3:]) and not (1 in extremas[-3:])):
#         direction = 1  
#     print(direction)  
#     # plt.draw()
#     plt.pause(0.0001)
#     # plt.clf()
# input()
# for row in datax:
# data.append(row)
data = datax
plot(ax1, data)
# ys = np.array([x['Close'] for x in data])
# opens = [x['Open'] for x in data]
closes = [x['Close'] for x in data]
# ys = np.array([])
# yss = []
# for i in range(len(data)):
#     yss.append(opens[i])
#     yss.append(closes[i])
# ys = np.array(closes)
Yw = np.fft.rfft(closes)
Yw[9:] = 0
ys = np.fft.irfft(Yw, len(closes))

order = 18
# order = int(input('Order: '))
# if(order == 0):
#     break;
ax1.plot(ys, color='yellow')
maxids = argrelextrema(ys, np.greater, order=order, mode='clip')[0]
minids = argrelextrema(ys, np.less, order=order, mode='clip')[0]
# maxs = [(x, data[x]) for x in maxids]
# mins = [(x, data[x]) for x in minids]
ax1.vlines(maxids, mn, mx, colors='green')
ax1.vlines(minids, mn, mx, colors='red')
    # plt.pause(0.05)
extremas = [0]*len(data)
for maxid in maxids:
    extremas[round(maxid)] = 1
for minid in minids:
    extremas[round(minid)] = -1
print(extremas)
direction = None
if((1 in extremas[-3:]) and not (-1 in extremas[-3:])):
    direction = -1
elif((-1 in extremas[-3:]) and not (1 in extremas[-3:])):
    direction = 1  
print(direction)  
plt.show()
# plt.draw()
# plt.pause(0.0001)
# plt.clf()
# input()
# pdb.set_trace()