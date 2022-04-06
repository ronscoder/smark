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
    timestamp = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    if(timestamp.time() > datetime.time(hour=15, minute=15)):
        orderapi.exit_all_positions()
        return    
    position = p1.get('CURRENT_BUY_ORDER')
    if(position == None):
        return
    tradingsymbol = position['tradingsymbol']
    instrument_token = position['instrument_token']
    if(not channel == f'TICK_{instrument_token}'):
        return
    # print('trail SL check. position', tradingsymbol)
    price_bought = position['price']
    slorder = position['COUNTER_SL_ORDER']
    if(slorder == None):
        print('ERROR', 'NO SL SELL ORDER!')
        return
<<<<<<< HEAD
    # base_price = price_bought if price_bought > stoploss else stoploss
=======
    stoploss = slorder['price']
    base_price = price_bought if price_bought > stoploss else stoploss
    # base_price = stoploss
>>>>>>> 277ac858598eeed8d9bf40e3d7c029da7645c813
    # increment = math.floor(base_price * getConfig('TRAIL_PC'))
    # if time of hold is greater than certain duration, and exit.
    # order_time = datetime.datetime.fromisoformat(position['order_timestamp'])
    # now = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
    # timepast = now.replace(tzinfo=None) - order_time
    # exit_time = datetime.timedelta(minutes=configs['OPEN_ORDER_EXPIRY_MIN']*2)
    # if(timepast >= exit_time):
        # if(stoploss < price_bought):
            # pass
            # orderapi.modify_sl_order(order_id=position['COUNTER_SL_ORDER']['order_id'], price=round(ltp,1)-1, trigger=round(ltp,1)-1)
        # else:
            # orderapi.exit_position_market(order_id=position['COUNTER_SL_ORDER']['order_id'])
        # return
    configs = getConfigs()   
    stoploss = slorder['price']
    # base_price = stoploss  
    base_price = price_bought if price_bought > stoploss else stoploss       
    trigger = base_price + base_price * configs['TRAIL_BUFFER_PC']
    ltp = data['last_price']
    # newstoploss = math.floor(base_price * (1+getConfig('TRAIL_PC')))
    print('trail SL', tradingsymbol, 'base price', base_price, 'stoploss',stoploss, 'new trigger',trigger, 'ltp', ltp)
    if(ltp > trigger):
        newstoploss = round(base_price + (trigger - base_price)*configs['TRAIL_RATIO'],1)
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

if(__name__=='__main__'):
    print('running trail SL...')
    p1.subscribe(['TICK_*'], cb=action)
