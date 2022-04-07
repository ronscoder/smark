from libs.pubsub import get_ps_1
from libs.configs import getConfig
import logging
import datetime
from libs.orderapi import Orderapi
from setoptions import set_options
from truths import getTruthsOf
import time
from zoneinfo import ZoneInfo


logging.basicConfig(filename="logs/place_orders.log", level=logging.DEBUG)
ps1 = get_ps_1()
orderapi = Orderapi()


def place_orders():
    if(getConfig('HOLD_EXE')):
        print('Trade execution on hold by remote')
        return
    # market window
    timestamp = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    if(not (datetime.time(hour=9, minute=25) < timestamp.time() < datetime.time(hour=15, minute=5))):
        print('Outside market time window')
        logging.info('Outside market time window')
        return
    if(not getTruthsOf('BANKNIFTY')):
        return
    if(not getTruthsOf('GENERAL')):
        return
    # if(timestamp < direction['timestamp'] + datetime.timedelta(minutes=getConfig('OPEN_ORDER_EXPIRY_MIN'))):
    inst_ce, inst_pe = set_options(if_ce=True, if_pe=True)
    time.sleep(2)
    try:
        ce = inst_ce[0]
        orderapi.place_sl_buy_order(ce, getConfig('NIFTYBANK_QTY'), 'NFO')
        time.sleep(2)
        pe = inst_pe[0]
        orderapi.place_sl_buy_order(pe, getConfig('NIFTYBANK_QTY'), 'NFO')
        return [ce, pe]
    except Exception as ex:
        print('Error placing orders')
        print(ex.__str__())


def action(data):
    print('PLACE ORDERS checking...')
    oorders = orderapi.get_open_orders()
    if(len(oorders) == 0):
        #=> there is no open sell orders
        print('There is no position.', 'Placing order...')
        try:
            insts = place_orders()
            print('exe_boundary', insts)
        except Exception as ex:
            print('Error placing orders')
            print(ex.__str__())
    else:
        pass

import threading
def subscribe_pexit():
    ps1.subscribe(['POSITION_EXITED'], action)

if(__name__ == '__main__'):
    print('Place order started')
    t0 = threading.Thread(target=subscribe_pexit, daemon=True)
    
    while(True):
        action(True)
        wait_min = getConfig('OHLC_MIN')
        time.sleep(wait_min)
    

