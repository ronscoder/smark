import datetime
from libs.configs import getConfig
from libs.pubsub import get_ps_1
from libs.init_kite import getKite
import pdb

def set_options(if_ce=True, if_pe=True):
    # pdb.set_trace()
    # delConfig('NIFTYBANK_CE')
    # delConfig('NIFTYBANK_PE')
    price_range = getConfig('OPTION_PRICE_RANGE')
    kite, kw = getKite()
    niftybank_token = 260105
    IN_CHANNEL = f'TICK_{niftybank_token}'
    tick = get_ps_1().get(IN_CHANNEL)
    if(tick is None):
        print('tick is None')
        return
    nifty_bank_ltp = tick['last_price']
    # print(nifty_bank_ltp)
    atm_ = int(nifty_bank_ltp - nifty_bank_ltp % 100)
    atm = atm_ if (nifty_bank_ltp - atm_) < (atm_ +
                                             100 - nifty_bank_ltp) else atm_ + 100
    # print(atm)
    today = datetime.datetime.today()
    yy = today.strftime('%y')
    strikes = getConfig('STRIKES')

    insts = []
    for strike in strikes:
        msuffix = strike['suffix']
        strike_min = strike['min']
        strike_max = strike['max']
        options = []
        if(if_ce):
            options = [f'BANKNIFTY{yy}{msuffix}{x}CE' for x in range(atm, strike_max, 100)]
            insts.extend(options)
        if(if_pe):
            options = [f'BANKNIFTY{yy}{msuffix}{x}PE' for x in range(strike_min, atm, 100)]
            insts.extend(options)

    ltps = kite.ltp([f'NFO:{inst}' for inst in insts])

    for ltp in ltps:
        print(ltp, ltps[ltp]['last_price'])
    # print(ltps)
    
    ce = None
    if(if_ce):
        celtps = [(x, ltps[x]) for x in ltps if x[-2:] == 'CE']
        celtps = [x for x in sorted(celtps, key=lambda x: x[1]['last_price']) if (
            price_range[0] <= x[1]['last_price'] <= price_range[1])]
        if(len(celtps) > 0):
            for ce in celtps:
                print(ce[0], ce[1]['last_price'])
            print(celtps[-1])
            # symbol, token
            ce = (celtps[-1][0][4:], celtps[-1][1]['instrument_token'])
    print()
    pe = None
    if(if_pe):
        peltps = [(x, ltps[x]) for x in ltps if x[-2:] == 'PE']
        peltps = [x for x in sorted(peltps, key=lambda x: x[1]['last_price']) if (
            price_range[0] <= x[1]['last_price'] <= price_range[1])]
        if(len(peltps) > 0):
            for pe in peltps:
                print(pe[0], pe[1]['last_price'])
            print(peltps[-1])
            pe = (peltps[-1][0][4:], peltps[-1][1]['instrument_token'])
    
    return ce, pe


if(__name__ == '__main__'):
    set_options(True, True)
