from libs.configs import getConfig
from libs.pubsub import get_ps_1
import datetime
from libs.utilities import ydownload, get_last_working_day
from zoneinfo import ZoneInfo
import pandas as pd
from libs.calcs import get_extremas
from libs.configs import getConfig

p1 = get_ps_1('history profile')

def create_profile():
    order = getConfig['EXTREMA_ORDER']
    freqfact = getConfig['FREQ_CUTOFF_FACTOR']
    history = ydownload('^NSEBANK', startdate=get_last_working_day(days_offset=4))
    history['date'] = history.index.date
    gpidx  = set(history['date'])
    groups = []
    for idx in gpidx:
        df = history[history['date']==idx]
        extremas, _ = get_extremas(df['Close'].values, freqfact, order)
        
    