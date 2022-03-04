from kiteconnect.connect import KiteConnect as KC
from libs.pubsub import get_ps_1
from libs.init_kite import getKite
from libs.configs import getConfig
import sched
import time
# import logging

# # logging.basicConfig(filename='logs/orderapi.log', level=logging.DEBUG)


class Orderapi:
    def __init__(self) -> None:
        self.kite, _ = getKite()
        self.r1 = get_ps_1()

    def get_open_orders(self):
        if(self.kite is None):
            print('Error in Order API')
            return
        orders = self.kite.orders()
        return [x for x in orders if x['status'] == 'TRIGGER PENDING']

    def get_open_buy_orders(self):
        if(self.kite is None):
            print('Error in Order API')
            return
        orders = self.kite.orders()
        return [x for x in orders if x['status'] == 'TRIGGER PENDING' and x['transaction_type'] == 'BUY']

    def get_open_sell_orders(self):
        if(self.kite is None):
            print('Error in Order API')
            return
        orders = self.kite.orders()
        return [x for x in orders if x['status'] == 'TRIGGER PENDING' and x['transaction_type'] == 'SELL']

    def cancel_open_buy_orders(self):
        print('cancel open buy orders')
        open_orders = self.get_open_buy_orders()
        for order in open_orders:
            print('cancelling open order', order['tradingsymbol'])
            if(self.kite is None):
                print('Error in Order API')
                return
            self.kite.cancel_order(
                order['variety'], order['order_id'])

    def cancel_position(self):
        position = self.r1.hgetall('CURRENT_POSITION')
        if(position is not None):
            if(self.kite is None):
                print('Error in Order API')
                return
            # self.kite.orders()
            # logging.info('cancelling open order')
            # logging.info(position)
            if(self.kite is None):
                print('Error in Order API')
                return
            orders = self.kite.orders()
            order = [x for x in orders if x['order_id']
                     == position['order_id']][0]
            if(order['status'] == 'OPEN'):
                if(self.kite is None):
                    print('Error in Order API')
                    return
                self.kite.cancel_order(
                    position['variety'], position['order_id'])

    def modify_sl_order(self, order_id, price, trigger):
        params = dict(variety=KC.VARIETY_REGULAR, order_id=order_id,
                      order_type=KC.ORDER_TYPE_SL, price=price, trigger_price=trigger)
        # logging.info('modifying SL order')
        # logging.info(params)
        if(self.kite is None):
            print('Error in Order API')
            return
        self.kite.modify_order(**params)

    def position_scheduler(self):
        s = sched.scheduler(time.time, time.sleep)
        s.enter(getConfig('OPEN_ORDER_EXPIRY_MIN')*60,
                1, self.cancel_open_buy_orders)
        s.run()

    def place_sl_sell_order(self, orderdata):
        print('place SL sell order', orderdata['tradingsymbol'])
        price, stoploss_trigger = self.get_sell_sl_prices(orderdata['tradingsymbol'],orderdata['exchange'], orderdata['price'])
        if(self.kite is None):
            print('Error in Order API')
            return
        params = {'variety': orderdata['variety'], "exchange": orderdata['exchange'], "tradingsymbol": orderdata['tradingsymbol'], "transaction_type": self.kite.TRANSACTION_TYPE_SELL,
                  "quantity": orderdata['quantity'], "order_type": self.kite.ORDER_TYPE_SL, "product": orderdata['product'], "price": price, 'trigger_price': stoploss_trigger}
        print('trigger', stoploss_trigger, 'price', price)
        if(self.kite is None):
            print('Error in Order API')
            return
        order_id = self.kite.place_order(**params)


    def get_sell_sl_prices(self, tradingsymbol, exchange, price_bought=0):
        if(self.kite is None):
            print('Error in Order API')
            return
        kite = self.kite
        symb = f'{exchange}:{tradingsymbol}'
        if(price_bought == 0):
            last_price = kite.ltp(symb)[symb]['last_price']
        else:
            last_price = price_bought
        price = round((1 - float(getConfig('STOP_PC')))*last_price, 1)
        trigger = price + getConfig('TRIGGER_GAP')
        return (price, trigger)

    def get_buy_sl_prices(self, tradingsymbol, exchange):
        if(self.kite is None):
            print('Error in Order API')
            return
        kite = self.kite
        symb = f'{exchange}:{tradingsymbol}'
        last_price = kite.ltp(symb)[symb]['last_price']
        price = round((1+float(getConfig('ENTRY_STOP_PC')))*last_price, 1)
        trigger = round(price - float(getConfig('TRIGGER_GAP')),1)
        return (price, trigger)

    def place_sl_buy_order(self, instsymbol, qty, exchange, price=0):
        if(self.kite is None):
            print('Error in Order API')
            return
        kite = self.kite
        order_price, trigger = self.get_buy_sl_prices(instsymbol, exchange)
        if(not price == 0):
            order_price = price
            trigger = price - getConfig('TRIGGER_GAP')
        try:
            print('placing order', instsymbol, f'{order_price}/{trigger}')
            position = dict(variety=kite.VARIETY_REGULAR, exchange=exchange, tradingsymbol=instsymbol,
                            transaction_type=kite.TRANSACTION_TYPE_BUY, quantity=qty, product=kite.PRODUCT_MIS, order_type=kite.ORDER_TYPE_SL, price=order_price, trigger_price=trigger)
            order_id = kite.place_order(**position)

        except Exception as ex:
            print('Error placing order', instsymbol, ex.__str__())
