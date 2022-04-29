import datetime
from libs.configs import getConfig
from libs.pubsub import get_ps_1
from libs.init_kite import getKite
import pdb
from libs.utilities import is_holiday

def get_next_thursday_date(week=0):
    today = datetime.datetime.today()
    days_to_next_thursday = 7*week + 3 - today.weekday()
    date = today + datetime.timedelta(days=days_to_next_thursday)
    if(is_holiday(date)):
        date = date - datetime.timedelta(days=1)
    return date

def filter_ce(ltps, price_range):
    for ltp in ltps:
        print(ltp, ltps[ltp]['last_price'])
    celtps = [(x, ltps[x]) for x in ltps if x[-2:] == 'CE']
    celtps = [x for x in sorted(celtps, key=lambda x: x[1]['last_price']) if (
        price_range[0] <= x[1]['last_price'] <= price_range[1])]
    if(len(celtps) > 0):
        for ce in celtps:
            print(ce[0], ce[1]['last_price'])
        print(celtps[-1])
        # symbol, token
        ce = (celtps[-1][0][4:], celtps[-1][1]['instrument_token'])
        return ce

def filter_pe(ltps, price_range):
    for ltp in ltps:
        print(ltp, ltps[ltp]['last_price'])    
    peltps = [(x, ltps[x]) for x in ltps if x[-2:] == 'PE']
    peltps = [x for x in sorted(peltps, key=lambda x: x[1]['last_price']) if (
        price_range[0] <= x[1]['last_price'] <= price_range[1])]
    if(len(peltps) > 0):
        for pe in peltps:
            print(pe[0], pe[1]['last_price'])
        print(peltps[-1])
        pe = (peltps[-1][0][4:], peltps[-1][1]['instrument_token'])
        return pe

def get_strikes():
    pass

def set_options(if_ce=True, if_pe=True):
    # pdb.set_trace()
    # delConfig('NIFTYBANK_CE')
    # delConfig('NIFTYBANK_PE')
    price_range = getConfig('OPTION_PRICE_RANGE')
    kite, kw = getKite()
    niftybank_token = 260105
    IN_CHANNEL = f'TICK_{niftybank_token}'
    tick = get_ps_1('setoptions').get(IN_CHANNEL)
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

    ce = None
    pe = None

    next_thursday_1 = get_next_thursday_date(0)
    mdd_current_week = f'{next_thursday_1.month}{next_thursday_1.day:02}'
    # if(not (mdd_current_week == f'{today.month}{today.day:02}')):
    if(strikes['CURRENT_WEEK']['ALL']):
        low = atm - 40 * 100
        high = atm + 40 * 100
    else:
        low = strikes['CURRENT_WEEK']['LOW']
        high = strikes['CURRENT_WEEK']['HIGH']
    if(if_ce):
        options = [f'BANKNIFTY{yy}{mdd_current_week}{x}CE' for x in range(atm, high, 100)]
        ltps = kite.ltp([f'NFO:{inst}' for inst in options])
        ce = filter_ce(ltps, price_range)
    
    if(if_pe):
        options = [f'BANKNIFTY{yy}{mdd_current_week}{x}PE' for x in range(low, atm, 100)]
        ltps = kite.ltp([f'NFO:{inst}' for inst in options])
        pe = filter_pe(ltps, price_range)
    # pdb.set_trace()
    if(None in [ce, pe]):
        next_thursday_2 = get_next_thursday_date(1)

        mdd_next_week = f'{next_thursday_2.month}{next_thursday_2.day:02}'
        if(strikes['NEXT_WEEK']['ALL']):
            low = atm - 40 * 100
            high = atm + 40 * 100
        else:
            low = strikes['NEXT_WEEK']['LOW']
            high = strikes['NEXT_WEEK']['HIGH']
        if(if_ce and ce is None):
            options = [f'BANKNIFTY{yy}{mdd_next_week}{x}CE' for x in range(atm, high, 100)]
            ltps = kite.ltp([f'NFO:{inst}' for inst in options])
            ce = filter_ce(ltps, price_range)
        if(if_pe and pe is None):
            options = [f'BANKNIFTY{yy}{mdd_next_week}{x}PE' for x in range(low, atm, 100)]
            ltps = kite.ltp([f'NFO:{inst}' for inst in options])
            pe = filter_pe(ltps, price_range)
    
    if(None in [ce, pe]):
        mmm_current_month = f'{today.strftime("%b").upper()}'
        if(strikes['CURRENT_MONTH']['ALL']):
            low = atm - 40 * 100
            high = atm + 40 * 100
        else:
            low = strikes['CURRENT_MONTH']['LOW']
            high = strikes['CURRENT_MONTH']['HIGH']
        if(if_ce and ce is None):
            options = [f'BANKNIFTY{yy}{mmm_current_month}{x}CE' for x in range(atm, high, 100)]
            ltps = kite.ltp([f'NFO:{inst}' for inst in options])
            ce = filter_ce(ltps, price_range)
        if(if_pe and pe is None):
            options = [f'BANKNIFTY{yy}{mmm_current_month}{x}PE' for x in range(low, atm, 100)]
            ltps = kite.ltp([f'NFO:{inst}' for inst in options])
            pe = filter_pe(ltps, price_range)
    return ce, pe


if(__name__ == '__main__'):
    print(set_options(True, True))
