from unittest import expectedFailure
from libs.pubsub import get_ps_1
from libs.configs import getConfig, getConfigs
from libs.orderapi import Orderapi
import datetime
from zoneinfo import ZoneInfo

p1 = get_ps_1('trailsl')
orderapi = Orderapi()
nifty_token = 260105

def action(channel, data, position):
    # instrument_token = data['instrument_token']
    # if(instrument_token == nifty_token):
    #     return
    # print('checking tick for new TRAIL')
    # timestamp = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    # if(timestamp.time() > datetime.time(hour=15, minute=15)):
    #     orderapi.exit_all_positions()
    #     return    
    # position = p1.get('CURRENT_BUY_ORDER')
    # if(position == None):
    #     return
    tradingsymbol = position['tradingsymbol']
    # instrument_token = position['instrument_token']
    # if(not channel == f'TICK_{instrument_token}'):
    #     return
    # print('trail SL check. position', tradingsymbol)
    price_bought = position['price']
    if(not 'COUNTER_SL_ORDER' in position):
        print('ERROR', 'NO SL SELL ORDER!')
        return
    slorder = position['COUNTER_SL_ORDER']

    configs = getConfigs()   
    stoploss = slorder['price']
    # base_price = stoploss  
    base_price = price_bought if price_bought > stoploss else stoploss       
    trigger = round(base_price + base_price * configs['TRAIL_BUFFER_PC'],1)
    ltp = data['last_price']
    # newstoploss = math.floor(base_price * (1+getConfig('TRAIL_PC')))
    newstoploss = round(base_price + (trigger - base_price)*configs['TRAIL_RATIO'],1)
    print('trail SL', tradingsymbol, 'base price', base_price, 'stoploss',stoploss, 'new trigger',f'{newstoploss}/{trigger}', 'ltp', ltp)
    if(ltp > trigger):
        # unit_pl = ltp - base_price
        # factor = unit_pl//increment
        # newstoploss = base_price + increment * factor
        print(f'{tradingsymbol} set new stoploss from {base_price} -> {newstoploss}->{trigger}')
        try:
            orderapi.modify_sl_order(order_id=position['COUNTER_SL_ORDER']['order_id'], price=newstoploss, trigger=newstoploss)
        except Exception as ex:
            print('Error modifying SL Sell order')
            print(ex.__str__())
    else:
        
        pass
def cb(channel, data, container = {}):
    instrument_token = data['instrument_token']
    if(instrument_token == nifty_token):
        return
    position = p1.get('CURRENT_BUY_ORDER')
    if(position == None):
        return
    instrument_token = position['instrument_token']
    if(not channel == f'TICK_{instrument_token}'):
        return    
    last_timestamp = container.get('last_timestamp', None)
    timestamp = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    if(last_timestamp is not None):
        tdelta = timestamp - last_timestamp
        if(tdelta > datetime.timedelta(minutes = getConfig('OHLC_MIN'))):
            print('Trailing SL, time delta', tdelta)
            container = {}
            try:
                action(channel, data, position)
            except Exception as ex:
                print('Error in trail sl')
                print(ex.__str__())
    else:
        container['last_timestamp'] = timestamp
    if(timestamp > datetime.time(hour=15, minute=15)):
        orderapi.exit_all_positions()
    
    
if(__name__=='__main__'):
    print('running trail SL...')
    container = {}
    p1.subscribe(['TICK_*'], cb=lambda channel, data: cb(channel, data, container))
