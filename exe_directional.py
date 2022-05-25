from libs.pubsub import get_ps_1
from libs.configs import getConfig, getConfigs
import logging
import datetime
from libs.orderapi import Orderapi
from setoptions import set_options
from zoneinfo import ZoneInfo


logging.basicConfig(filename="logs/place_orders.log", level=logging.DEBUG)

class Action:
    def __init__(self) -> None:
        # self.configs = getConfigs()
        self.last_exit = 0
        self.direction = 0 
        self.orderapi = Orderapi()
        self.ps1 = get_ps_1('exe directional')
        
    def place_orders(self, direction):
        if(getConfig('HOLD_EXE')):
            print('Trade execution on hold by remote')
            return
        # market window
        timestamp = datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata'))
        if(not (datetime.time(hour=9, minute=15) < timestamp.time() < datetime.time(hour=15, minute=5))):
            print('Outside market time window')
            logging.info('Outside market time window')
            return

        if(not getConfig('DIRECTIONAL_EXE')):
            print('Directional trade not activated')
            return
        option = None
        inst = None
        if(direction == 1):    
            inst, _ = set_options(if_ce=False, if_pe=True)
        elif(direction == -1):
            _, inst = set_options(if_ce=True, if_pe=False)

        if(not inst is None):
            option = inst[0]
            try:
                self.orderapi.place_sl_buy_order(option, getConfig('NIFTYBANK_QTY'), 'NFO')
            except Exception as ex:
                print('Error placing orders')
                print(ex.__str__())
            return option
        else:
            print('No suitable option instrument found')
        

    def action(self, channcel, data):
        direction = self.direction = data['direction'] if 'direction' in data else 0
        timestamp = data['timestamp']
        print('direction', timestamp, direction)
        if(direction is None):
            return
        try:
            oorders = self.orderapi.get_open_orders()
        except Exception as ex:
            print('[exe_directional] Error', ex.__str__())
            return
        osellorders = [x for x in oorders if x['status'] == 'TRIGGER PENDING' and x['transaction_type'] == 'SELL']    
        obuyorders = [x for x in oorders if x['status'] == 'TRIGGER PENDING' and x['transaction_type'] == 'BUY']
        # if open sell order and direction doesnot match, exist
        if(len(osellorders)>0):
            for order in osellorders:
                position_direction = 1 if order['tradingsymbol'][-2:] == 'CE' else -1
                if(position_direction != direction):
                    #exit reversal
                    self.orderapi.exit_all_positions([order])
                    return
        else:
            # no position
            if(len(obuyorders)>0):
                for order in obuyorders:
                    position_direction = 1 if order['tradingsymbol'][-2:] == 'CE' else -1
                    if(position_direction == direction):
                    #exit reversal
                        self.orderapi.cancel_open_buy_orders([order])
                    else:
                        pass
            else:
                # place new order
                print('No position.', 'Placing new order...')
                try:
                    insts = self.place_orders(direction)
                    print('insts exe_directional', insts)
                except Exception as ex:
                    print('Error placing orders')
                    print(ex.__str__())
if(__name__ == '__main__'):
    print('Directional place order started')
    action = Action()
    action.ps1.subscribe(['BANKNIFTY_DIRECTION'], action.action)

