from libs.pubsub import get_ps_1
from libs.configs import getConfig, getConfigs
from libs.orderapi import Orderapi
import datetime
from zoneinfo import ZoneInfo

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
    # increment = math.floor(base_price * getConfig('TRAIL_PC'))
    # if time of hold is greater than certain duration, and exit.
    configs = getConfigs()
    order_time = datetime.datetime.fromisoformat(position['order_timestamp'])
    now = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    timepast = now.replace(tzinfo=None) - order_time
    exit_time = datetime.timedelta(minutes=configs['OPEN_ORDER_EXPIRY_MIN']*2)
    if(timepast >= exit_time):
        if(ltp >= base_price):
            orderapi.modify_sl_order(order_id=position['COUNTER_SL_ORDER']['order_id'], price=round(ltp,1)-1, trigger=round(ltp,1)-1)
        else:
            orderapi.exit_position_market(order_id=position['COUNTER_SL_ORDER']['order_id'])
        return
    trigger = base_price + base_price * configs['TRAIL_BUFFER_PC']
    # newstoploss = math.floor(base_price * (1+getConfig('TRAIL_PC')))
    print('trail SL', tradingsymbol, 'base price', base_price, 'stoploss',stoploss, 'new trigger',trigger, 'ltp', ltp)
    if(ltp > trigger):
        newstoploss = round(trigger*configs['TRAIL_RATIO'],1)
        # unit_pl = ltp - base_price
        # factor = unit_pl//increment
        # newstoploss = base_price + increment * factor
        print(f'{tradingsymbol} set new stoploss from {base_price} -> {newstoploss}->{trigger}')
        try:
            orderapi.modify_sl_order(order_id=position['COUNTER_SL_ORDER']['order_id'], price=newstoploss, trigger=newstoploss)
            position['COUNTER_SL_ORDER']['trigger_price'] = newstoploss
            position['COUNTER_SL_ORDER']['price'] = newstoploss
            p1.set('CURRENT_BUY_ORDER', position)
        except Exception as ex:
            print('Error modifying SL Sell order')
            print(ex.__str__())
    else:
        
        pass

if(__name__=='__main__'):
    print('running trail SL...')
    p1.subscribe(['TICK_*'], cb=action)
