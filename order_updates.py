from libs.pubsub import get_ps_1
from kiteconnect import KiteConnect as KC
from libs.orderapi import Orderapi
from libs.init_kite import getKite
import logging
import time

logging.basicConfig(filename="logs/order_updates.log", level=logging.DEBUG)

ps1 = get_ps_1()
channels = ['ORDER_UPDATE']

kite, kw = getKite()
orderApi = Orderapi()

def handle_order_update(channel, data):

    '''
    {'account_id': 'YZ7009', 'unfilled_quantity': 0, 'checksum': '', 'placed_by': 'YZ7009', 'order_id': '210429201339323', 'exchange_order_id': '1300000005271142', 'parent_order_id': None, 'status': 'OPEN', 'status_message': None, 'status_message_raw': None, 'order_timestamp': '2021-04-29 10:06:02', 'exchange_update_timestamp': '2021-04-29 10:06:02', 'exchange_timestamp': '2021-04-29 10:06:02', 'variety': 'regular', 'exchange': 'NSE', 'tradingsymbol': 'TATAPOWER', 'instrument_token': 877057, 'order_type': 'MARKET', 'transaction_type': 'BUY', 'validity': 'DAY', 'product': 'MIS', 'quantity': 1, 'disclosed_quantity': 0, 'price': 0, 'trigger_price': 0, 'average_price': 0, 'filled_quantity': 0, 'pending_quantity': 1, 'cancelled_quantity': 0, 'market_protection': 0, 'meta': {}, 'tag': None, 'guid': '01XasEtN1HNSVNN'}
    Expected data
    exchange entry update: completed, rejected, open, pending...
    gtt status

    '''
    txntype = data['transaction_type']
    status = data['status']
    tradingsymbol = data['tradingsymbol']
    order_id = data['order_id']
    qty = data['quantity']
    product = data['product']
    exchange = data['exchange']
    # order_timestamp = data['order_timestamp']
    instrument_token = data['instrument_token']
    trigger_price = data['trigger_price']
    price = data['price']

    "ensure this handles only options"
    # print(data)
    print(tradingsymbol, txntype, status)
    logging.info(data)
    
    if(not product == KC.PRODUCT_MIS):
        print('skipping non MIS product')
        return
    #1:
    'Entry order, explicitly for options'
    if(txntype == KC.TRANSACTION_TYPE_BUY):
        # 'get existing position'
        # position = ps1.get('CURRENT_BUY_ORDER')
        # if(not position is None):
        #     ps1.set('CURRENT_BUY_ORDER', data)
        if(status == 'OPEN'):
            pass
        if(status == KC.STATUS_CANCELLED):
            pass

        if(status == KC.STATUS_REJECTED):
            pass
        
        if(status == 'TRIGGER PENDING'):
            pass

        if(status == KC.STATUS_COMPLETE):
            # ps1.publish('SMARKMSG', f'bought {tradingsymbol} @ {price}')
            ps1.set('CURRENT_BUY_ORDER', data)
            orderApi.place_sl_sell_order(data)
            time.sleep(1)
            orderApi.cancel_open_buy_orders()

    if(txntype == KC.TRANSACTION_TYPE_SELL):
        if(status == 'TRIGGER PENDING'):
            'update counter sell order'
            buy_order = ps1.get('CURRENT_BUY_ORDER')
            buy_order['COUNTER_SL_ORDER'] = {'order_id': order_id, 'trigger_price': trigger_price, 'price': price}
            ps1.set('CURRENT_BUY_ORDER', buy_order)
            print(buy_order)
            # Activate driver for trailing SL
            ps1.publish('resubscription_tokens', {'flag':1, 'token': instrument_token})

        if(status == KC.STATUS_CANCELLED):
            pass
        if(status == KC.STATUS_REJECTED):
            print('ERROR', 'Sell order rejected')
            pass

        if(status == KC.STATUS_COMPLETE):
            # ps1.publish('SMARKMSG', f'sold {tradingsymbol} @ {price}')
            # order = ps1.get('CURRENT_BUY_ORDER')
            # try:
            #     pl = price - order['price']
            #     ps1.publish('SMARKMSG', f'profit/loss {tradingsymbol} @ {round(pl,1)*qty}')
            # except:
            #     pass
            ps1.r.delete('CURRENT_BUY_ORDER')
            ps1.publish('resubscription_tokens', {'flag':-1, 'token': instrument_token})
            ps1.publish('POSITION_EXITED', True)
            # place_orders()

        if(status == 'OPEN'):
            pass
            
            
if(__name__ == '__main__'):
    print('running order updates...')
    ps1.subscribe(channels, handle_order_update)