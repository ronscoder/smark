from libs.configs import getConfig, setConfig
from libs.pubsub import get_ps_1
import datetime
from libs.init_kite import getKite
from libs.configs import delConfig
import pdb

def set_options():
    # pdb.set_trace()
    delConfig('NIFTYBANK_CE')
    delConfig('NIFTYBANK_PE')
    price_range = getConfig('OPTION_PRICE_RANGE')
    kite, kw = getKite()
    niftybank_token = 260105
    IN_CHANNEL = f'TICK_{niftybank_token}'
    tick = get_ps_1().get(IN_CHANNEL)
    if(tick is None):
        return
    nifty_bank_ltp = tick['last_price']
    # print(nifty_bank_ltp)
    atm_ = int(nifty_bank_ltp - nifty_bank_ltp%100)
    atm = atm_ if (nifty_bank_ltp - atm_) < (atm_ + 100 - nifty_bank_ltp) else atm_ + 100
    # print(atm)
    yy = '22'
    'next thursdays'
    # dds = getConfig('THURSDAYS')
    mds = getConfig('OPTION_MD')
    d = datetime.datetime.now()
    # ms = [d.month, d.month+1] #not allow
    # ms = [d.month]
    b = datetime.datetime.strftime(d, "%b").upper()
    # # print(month)
    ce_strike_from = atm + getConfig('STRIKE_MID_SKIP')
    ce_strike_upto = ce_strike_from + getConfig('STRIKE_LIMIT')
    print('CE strike range', ce_strike_from, ce_strike_upto)
    ces = [f'BANKNIFTY{yy}{md[0]}{md[1]}{strike}CE' for strike in range(ce_strike_from, ce_strike_upto, 100) for md in mds] + [f'BANKNIFTY{yy}{b}{strike}CE' for strike in range(ce_strike_from, ce_strike_upto, 100)]
    # print(ces)

    pe_strike_from = atm - getConfig('STRIKE_MID_SKIP') - getConfig('STRIKE_LIMIT')
    pe_strike_upto = pe_strike_from + getConfig('STRIKE_LIMIT')
    print('PE strike range', pe_strike_from, pe_strike_upto)
    pes = [f'BANKNIFTY{yy}{md[0]}{md[1]}{strike}PE' for strike in range(pe_strike_from, pe_strike_upto, 100) for md in mds] + [f'BANKNIFTY{yy}{b}{strike}PE' for strike in range(pe_strike_from, pe_strike_upto, 100)]
    # print(pes)
    # pdb.set_trace()
    ltps = kite.ltp([f'NFO:{inst}' for inst in [*ces, *pes]])
    # print('rate', rate)
    for ltp in ltps:
        print(ltp, ltps[ltp]['last_price'])
    # print(ltps)
    print()
    celtps = [(x, ltps[x]) for x in ltps if x[-2:] == 'CE']
    celtps = [x for x in sorted(celtps, key=lambda x: x[1]['last_price']) if (price_range[0] <= x[1]['last_price'] <= price_range[1])]
    if(len(celtps)>0):
        for ce in celtps:
            print(ce[0], ce[1]['last_price'])
        print(celtps[-1])
        # symbol, token
        setConfig('NIFTYBANK_CE', (celtps[-1][0][4:], celtps[-1][1]['instrument_token']))
    print()
    peltps = [(x, ltps[x]) for x in ltps if x[-2:] == 'PE']
    peltps = [x for x in sorted(peltps, key=lambda x: x[1]['last_price']) if (price_range[0] <= x[1]['last_price'] <= price_range[1])]
    if(len(peltps)>0):
        for pe in peltps:
            print(pe[0], pe[1]['last_price'])
        print('PE')
        print(peltps[-1])
        setConfig('NIFTYBANK_PE', (peltps[-1][0][4:],peltps[-1][1]['instrument_token']))
    

if(__name__ == '__main__'):
    set_options()