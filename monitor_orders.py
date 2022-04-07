# Monitor and update the price and triggers for open orders
import time
from libs.orderapi import Orderapi
from libs.configs import getConfig
import datetime
from zoneinfo import ZoneInfo


orderapi = Orderapi()

def action(data):
    oorders = orderapi.get_open_orders()
    obuyorders = [x for x in oorders if x['transaction_type']=='BUY']
    if(len(obuyorders)>0):
        print('There are open buy orders', len(obuyorders))
        now = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
        expiry_min = getConfig('OPEN_ORDER_EXPIRY_MIN')
        candle_min = getConfig('OHLC_MIN')
        for order in obuyorders:
            order_time = order['order_timestamp']
            timepast = now.replace(tzinfo=None) - order_time
            if(timepast > datetime.timedelta(minutes=expiry_min)):
                print('Canceling expired open buy orders', expiry_min)
                orderapi.cancel_open_buy_orders()
            # elif(timepast > datetime.timedelta(minutes=round(expiry_min/2-1))):
            elif(timepast > datetime.timedelta(minutes=candle_min)):
                print('Changing open buy order triggers')
                price, trigger = orderapi.get_buy_sl_prices(order['tradingsymbol'], order['exchange'])
                print(order['tradingsymbol'], 'new price', f'{price}/{trigger}')
                orderapi.modify_sl_order(order['order_id'], price, trigger)
if(__name__ == '__main__'):
    print('Monitor order started')
    while(True):
        action(None)
        wait_min = getConfig('OHLC_MIN')
        time.sleep(round(wait_min*1)*60)
