from libs.pubsub import get_ps_1
from libs.configs import getConfig
import logging
import datetime
from libs.orderapi import Orderapi
from setoptions import set_options
from truths import getTruthsOf
import time

logging.basicConfig(filename="logs/place_orders.log", level=logging.DEBUG)
ps1 = get_ps_1()
orderapi = Orderapi()


def place_orders():
    # market window
    if(not (datetime.time(hour=9, minute=20) < datetime.datetime.now().time() < datetime.time(hour=15, minute=5))):
        print('Outside market time window')
        logging('Outside market time window')
        return
    if(not getTruthsOf('BANKNIFTY')):
        return
    if(not getTruthsOf('GENERAL')):
        return
    # place intraday orders
    set_options()
    ce = getConfig(f'NIFTYBANK_CE')[0]
    orderapi.place_sl_buy_order(ce, getConfig('NIFTYBANK_QTY'), 'NFO')
    pe = getConfig(f'NIFTYBANK_PE')[0]
    orderapi.place_sl_buy_order(pe, getConfig('NIFTYBANK_QTY'), 'NFO')


if(__name__ == '__main__'):
    cancel_open_order_counter = 0
    while True:
        'Change price and trigger for open buy orders'
        oorders = orderapi.get_open_orders()
        obuyorders = [x for x in oorders if x['transaction_type']=='BUY']
        for order in obuyorders:
            price, trigger = orderapi.get_buy_sl_prices(order['tradingsymbol'])
            print('new price', f'{price}/{trigger}')
            orderapi.modify_sl_order(order['order_id'], price, trigger)
        if(len(oorders) == 0):
            try:
                place_orders()
            except Exception as ex:
                print('Error placing orders')
                print(ex.__str__())
        time.sleep(getConfig('OPEN_ORDER_EXPIRY_MIN')*60)
        cancel_open_order_counter += 1
        if(len(obuyorders) > 0 and cancel_open_order_counter%2 == 0):
            orderapi.cancel_open_buy_orders()
            cancel_open_order_counter = 0
