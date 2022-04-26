from libs.pubsub import get_ps_1
from libs.configs import getConfig, getConfigs
import logging
import datetime
from libs.orderapi import Orderapi
from setoptions import set_options
from zoneinfo import ZoneInfo


logging.basicConfig(filename="logs/place_orders.log", level=logging.DEBUG)
ps1 = get_ps_1('exe directional')
orderapi = Orderapi()

class Action:
    def __init__(self) -> None:
        # self.configs = getConfigs()
        self.last_exit = 0
        
    def place_orders(self, direction):
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

        # if(not getTruthsOf('BANKNIFTY')):
        #     return
        # if(not getTruthsOf('GENERAL')):
        #     return
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
        

    def action(self, channcel, data):
        direction = data['direction'] if 'direction' in data else None
        previous = data['previous'] if 'previous' in data else None
        if_good_gap = data['if_good_gap'] if 'if_good_gap' in data else None
        if(self.last_exit > 0):
            self.last_exit -= 1
        print('last exit CD', self.last_exit)
        if(direction is None):
            return
        print('PLACE ORDERS checking...')
        oorders = orderapi.get_open_orders()
        osellorders = [x for x in oorders if x['status'] == 'TRIGGER PENDING' and x['transaction_type'] == 'SELL']    
        obuyorders = [x for x in oorders if x['status'] == 'TRIGGER PENDING' and x['transaction_type'] == 'BUY']
        # if open sell order and direction doesnot match, exist
        if(len(osellorders)>0):
            for order in osellorders:
                position_direction = 1 if order['tradingsymbol'][-2:] == 'CE' else -1
                if(position_direction != direction):
                    #exit reversal
                    orderapi.exit_all_positions([order])
                    #TODO exclude taking new position for this direction for extrema_window = configs['EXTREMA_WINDOW']
                    self.last_exit = getConfig('EXTREMA_WINDOW')
                else:
                    pass
        else:
            # no position
            if(len(obuyorders)>0):
                for order in obuyorders:
                    position_direction = 1 if order['tradingsymbol'][-2:] == 'CE' else -1
                    if(position_direction != direction):
                    #exit reversal
                        orderapi.cancel_open_buy_orders([order])
                    else:
                        pass
            else:
                # place new order
                print('There is no position.', 'Placing new order...')
                try:
                    if(self.last_exit == 0 and if_good_gap):
                        insts = self.place_orders(direction)
                        print('try exe_directional', insts)
                    else:
                        print('Place order aborted due to recent directional exit')
                except Exception as ex:
                    print('Error placing orders')
                    print(ex.__str__())

        # if(direction is not None):
            
        #     obuyorders = [x for x in oorders if x['status'] == 'TRIGGER PENDING' and x['transaction_type'] == 'BUY']
        #     if(len(obuyorders)>0):
        #         if(direction == previous):
        #             pass
        #         else:
        #             print('Cancelling reverse directional order')
        #             orderapi.exit_all_positions()
        #             orderapi.cancel_open_buy_orders()
        #     osellorders = [x for x in oorders if x['status'] == 'TRIGGER PENDING' and x['transaction_type'] == 'SELL']                
        #     if(len(osellorders) == 0):
        #         #=> there is no open sell orders
        #         print('There is no position.', 'Placing order...')
        #         try:
        #             insts = place_orders(direction)
        #             print('exe_directional', insts)
        #         except Exception as ex:
        #             print('Error placing orders')
        #             print(ex.__str__())
        #     else:
        #         pass

if(__name__ == '__main__'):
    print('Directional place order started')
    action = Action()
    ps1.subscribe(['BANKNIFTY_DIRECTION'], action.action)

