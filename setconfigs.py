# from libs.configs import getConfigs, setConfigs
from libs.configs import getConfigs, setConfigs

CONFIGS = {
    'TRAIL_PC': 0.05,
    'TRAIL_BUFFER_PC': 0.03,
    'ENTRY_STOP_PC': 0.2,
    'STOP_PC': 0.08,
    'TRIGGER_GAP': 1.0,
    'NIFTYBANK_QTY': 25,
    'HOLD_EXE': True,
    'OPTION_PRICE_RANGE': (50, 90),
    'STRIKE_MID_SKIP': 1000,
    'STRIKE_LIMIT': 1000,
    'DURATION_OPEN_POSITION_MIN': 120.0,
    'OPTION_MD': [('2','17'), ('3','03')],
    'OPEN_ORDER_EXPIRY_MIN': 7
}

def setDefaultConfigs():
    setConfigs(CONFIGS)

if(__name__ == '__main__'):
    setDefaultConfigs()