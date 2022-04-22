from kiteconnect import KiteConnect, KiteTicker
import datetime
from libs.configs import getConfig
from access import get_access_token


def getKite():
    token = get_access_token()
    if(token == None):
        print('No access token')
        return None, None
    kite = KiteConnect(api_key=getConfig('api_key'), access_token= token)
    kws = KiteTicker(getConfig('api_key'), token)
    return kite, kws
