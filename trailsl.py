from libs.pubsub import get_ps_1
from libs.configs import getConfig
import math
from libs.orderapi import Orderapi


p1 = get_ps_1()
orderapi = Orderapi()
nifty_token = 260105

def action(channel, data):
    instrument_token = data['instrument_token']
    if(instrument_token == nifty_token):
        return
    print('checking tick for new TRAIL')
    position = p1.get('CURRENT_BUY_ORDER')
    
    if(position == None):
        return

    tradingsymbol = position['tradingsymbol']
    instrument_token = position['instrument_token']
    if(not channel == f'TICK_{instrument_token}'):
        return
    # print('trail SL check. position', tradingsymbol)
    ltp = data['last_price']
    price_bought = position['price']
    slorder = position['COUNTER_SL_ORDER']
    if(slorder == None):
        print('ERROR', 'NO SL SELL ORDER!')
        return
    stoploss = slorder['price']
    base_price = price_bought if price_bought > stoploss else stoploss
    increment = math.floor(base_price * getConfig('TRAIL_PC'))
    newstoploss = base_price + increment
    # newstoploss = math.floor(base_price * (1+getConfig('TRAIL_PC')))
    print('trail SL', tradingsymbol, 'base price', base_price, 'new stoploss',newstoploss, 'ltp', ltp)
    if(ltp > (newstoploss + ltp*getConfig('TRAIL_BUFFER_PC'))):
        unit_pl = ltp - base_price
        factor = unit_pl//increment
        newstoploss = base_price + increment * factor
        print(f'{tradingsymbol} set new stoploss from {base_price} -> {newstoploss}')
        try:
            orderapi.modify_sl_order(order_id=position['COUNTER_SL_ORDER']['order_id'], price=newstoploss, trigger=newstoploss)
            position['COUNTER_SL_ORDER']['trigger_price'] = newstoploss
            position['COUNTER_SL_ORDER']['price'] = newstoploss
            p1.set('CURRENT_BUY_ORDER', position)
        except:
            pass

if(__name__=='__main__'):
    print('running trail SL...')
    p1.subscribe(['TICK_*'], cb=action)
