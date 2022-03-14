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


def place_orders(direction):
    
    if(getConfig('HOLD_EXE')):
        print('Trade execution on hold by remote')
        return
    # market window
    timestamp = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    if(not (datetime.time(hour=9, minute=20) < timestamp.time() < datetime.time(hour=15, minute=5))):
        print('Outside market time window')
        logging.info('Outside market time window')
        return
    if(not getTruthsOf('BANKNIFTY')):
        return
    if(not getTruthsOf('GENERAL')):
        return
    if(direction == None):
        print('No direction detected')
        return
    if(direction==1):
        # if(timestamp < direction['timestamp'] + datetime.timedelta(minutes=getConfig('OPEN_ORDER_EXPIRY_MIN'))):
        inst, _ = set_options(if_ce=True, if_pe=False)
        time.sleep(2)
        try:
            ce = inst[0]
            orderapi.place_sl_buy_order(ce, getConfig('NIFTYBANK_QTY'), 'NFO')
        except Exception as ex:
            print('Error placing orders for: ', inst)
            print(ex.__str__())
        return
    if(direction==-1):
        # if(timestamp < direction['timestamp'] + datetime.timedelta(minutes=getConfig('OPEN_ORDER_EXPIRY_MIN'))):
        _ , inst = set_options(if_ce=False, if_pe=True)
        time.sleep(2)
        try:
            pe = inst[0]
            orderapi.place_sl_buy_order(pe, getConfig('NIFTYBANK_QTY'), 'NFO')
        except Exception as ex:
            print('Error placing orders for: ', inst)
            print(ex.__str__())
        return


def action(channel, data):
    print(data)
    direction = data['direction']
    # timestamp = data['timestamp']
    'Change price and trigger for open buy orders'
    print('PLACE ORDERS checking...')
    oorders = orderapi.get_open_orders()
    if(len(oorders) == 0):
        #=> there is no open sell orders
        print('There is no position.', 'Placing order...')
        try:
            place_orders(direction)
        except Exception as ex:
            print('Error placing orders')
            print(ex.__str__())
        return
    now = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    expiry_min = getConfig('OPEN_ORDER_EXPIRY_MIN')
    obuyorders = [x for x in oorders if x['transaction_type']=='BUY']
    if(len(obuyorders) > 0):
        print('There are open buy orders', len(obuyorders))
        for order in obuyorders:
            order_time = order['order_timestamp']
            timepast = now.replace(tzinfo=None) - order_time
            if(timepast > datetime.timedelta(minutes=expiry_min)):
                print('Changing open buy order triggers')
                price, trigger = orderapi.get_buy_sl_prices(order['tradingsymbol'], order['exchange'])
                price_range = getConfig('OPTION_PRICE_RANGE')
                if(price in price_range):
                    print(order['tradingsymbol'], 'new price', f'{price}/{trigger}')
                    orderapi.modify_sl_order(order['order_id'], price, trigger)
                else:
                    print('Canceling expired open buy orders', expiry_min)
                    orderapi.cancel_open_buy_orders()
            # elif(timepast > datetime.timedelta(minutes=round(expiry_min/2))):

if(__name__ == '__main__'):
    print('Place order started')
    ps1.subscribe(['BANKNIFTY_DIRECTION'], action)

