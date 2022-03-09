from libs.orderapi import Orderapi
from libs.pubsub import get_ps_1
from libs.init_kite import getKite
import threading
from order_updates import handle_order_update
# from multiprocessing import process
'This is connection point to main server. and meant to run without interruptions and any complex calculations'
r = get_ps_1()

def connect():
    'This module is intended to run continuously. '
    kc, kws = getKite()
    
    def on_connect(ws, response):
        tokens = [260105,] #nifty bank
        print('[CONNECTED]')
        orders = Orderapi().get_open_sell_orders()
        for order in orders:
            tokens.append(order['instrument_token'])
        kws.subscribe(tokens)
        kws.set_mode(kws.MODE_FULL, tokens)
        print('subscribed tokens', kws.subscribed_tokens)
        # r.publish('STATUS', 'CONNECTED')

    def on_close(ws, code, reason):
        print('[CLOSED]', code, reason)
        # r.publish('STATUS', 'CLOSED')

    def on_ticks(ws, ticks):
        '''
        {'tradable': False, 'mode': 'full', 'instrument_token': 260105, 'last_price': 37392.05, 'ohlc': {'high': 37774.6, 'low': 37318.0, 'open': 37628.55, 'close': 37371.65}, 'change': 0.05458683253215058, 'exchange_timestamp': datetime.datetime(2022, 2, 23, 17, 28, 11)}
        '''
        for tick in ticks:
            # print(tick)
            # print(tick['instrument_token'],tick['last_price'],  end='\r')
            r.publish(f'TICK_{tick["instrument_token"]}', tick)
            # on_tick_handler(f'TICK_{tick["instrument_token"]}', tick)

    def on_error(ws, code, reason):
        print('[ERROR]', code, reason)
        # r.publish('STATUS', 'ERROR')

    def on_message(ws, payload, is_binary):
        pass

    def on_reconnect(ws, attempts_count):
        print('[RECONNECTING]')
        # r.publish('STATUS', 'RECONNECTED')

    def on_noreconnect(ws):
        print('NO RECONNECTION')
        kws.close()

    def on_order_update(ws, data):
        # r.publish('ORDER_UPDATE', data)
        handle_order_update('ORDER_UPDATE', data)
        

    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.on_ticks = on_ticks
    kws.on_error = on_error
    kws.on_message = on_message
    kws.on_reconnect = on_reconnect
    kws.on_noreconnect = on_noreconnect
    kws.on_order_update = on_order_update

    def _resubscribe(channel, data):
        # freshtokens = None
        # oldtokens = kws.subscribed_tokens
        add_or_remove = data['flag'] # -1 or 1
        token = data['token']
        if(add_or_remove == 1):
            print('subscribing to token', token)
            kws.subscribe([token])
            kws.set_mode(kws.MODE_FULL, [token])
        else:
            print('unsubscribing token', token)
            kws.unsubscribe([token])
            
        print('subscribed tokens')
        print(kws.subscribed_tokens)

    def resubscribe():
        print('subscribe token active')
        r.subscribe(['resubscription_tokens'], _resubscribe)

    # def _subscribe(channel, tokens):
    #     if(not channel == 'subscription_tokens'):
    #         return
    #     print('subscribing to', tokens)
    #     kws.subscribe(tokens)
    #     kws.set_mode(kws.MODE_FULL, tokens)
    #     print('subscribed tokens')
    #     print(kws.subscribed_tokens)

    # def subscribe():
    #     print('subscribe token active')
    #     r.subscribe(['subscription_tokens'], _subscribe)

    # def _unsubscribe(channel, tokens):
    #     if(not channel == 'unsubscription_tokens'):
    #         return
    #     print('unsubscribing tokens', tokens)
    #     try:
    #         kws.unsubscribe(tokens)
    #         # oldtokens = kws.subscribed_tokens
    #         # freshtokens = [x for x in oldtokens if x not in tokens]
    #         # kws.subscribe(freshtokens)
    #         # kws.set_mode(kws.MODE_FULL, freshtokens)
    #         print('subscribed tokens')
    #         print(kws.subscribed_tokens)
    #     except Exception as ex:
    #         print('ERROR', ex.__str__())


    # def unsubscribe():
    #     print('unsubscribe token active')
    #     r.subscribe(['unsubscription_tokens'], _unsubscribe)

    #TODO: 
    t0 = threading.Thread(target=resubscribe, daemon=True)
    # t1 = threading.Thread(target=subscribe, daemon=True)
    # t2 = threading.Thread(target=unsubscribe, daemon=True)
    # t2.start()
    # t1.start()
    t0.start()
    # process.ge
    kws.connect()

if __name__ == "__main__":
    connect()
