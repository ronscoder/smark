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
    if(not (datetime.time(hour=9, minute=25) < timestamp.time() < datetime.time(hour=15, minute=5))):
        print('Outside market time window')
        logging.info('Outside market time window')
        return

    if(not getConfig('DIRECTIONAL_EXE')):
        print('Directional trade not activated')
        return

    if(not getTruthsOf('BANKNIFTY')):
        return
    if(not getTruthsOf('GENERAL')):
        return
    # if(timestamp < direction['timestamp'] + datetime.timedelta(minutes=getConfig('OPEN_ORDER_EXPIRY_MIN'))):
    option = None
    inst = None
    if(direction == 1):    
        inst, _ = set_options(if_ce=True, if_pe=False)
    elif(direction == -1):
        _, inst = set_options(if_ce=False, if_pe=True)

    if(not inst is None):
        option = inst[0]
        try:
            orderapi.place_sl_buy_order(option, getConfig('NIFTYBANK_QTY'), 'NFO')
        except Exception as ex:
            print('Error placing orders')
            print(ex.__str__())
        return option
    


def action(channcel, data):
    direction = data['direction'] if 'direction' in data else None
    previous = data['previous'] if 'previous' in data else None
    print('PLACE ORDERS checking...')
    oorders = orderapi.get_open_orders()
    if(direction is not None):
        obuyorders = [x for x in oorders if x['status'] == 'TRIGGER PENDING' and x['transaction_type'] == 'BUY']
        if(len(obuyorders)>0):
            if(direction == previous):
                pass
            else:
                print('Cancelling reverse directional order')
                orderapi.cancel_open_buy_orders()
        osellorders = [x for x in oorders if x['status'] == 'TRIGGER PENDING' and x['transaction_type'] == 'SELL']                
        if(len(osellorders) == 0):
            #=> there is no open sell orders
            print('There is no position.', 'Placing order...')
            try:
                insts = place_orders(direction)
                print('exe_directional', insts)
            except Exception as ex:
                print('Error placing orders')
                print(ex.__str__())
        else:
            pass

if(__name__ == '__main__'):
    print('Directional place order started')
    ps1.subscribe(['BANKNIFTY_DIRECTION'], action)

