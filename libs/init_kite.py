from kiteconnect import KiteConnect, KiteTicker
import datetime
from libs.configs import getConfig
from libs.access import run_access


def getKite():
        run_access()
        access_token = getConfig('ACCESS_TOKEN')
        if(access_token is None):
            raise Exception('Acess token not set')
        tokendatestr, token = access_token.split(":")
        tokendate = datetime.date(int(tokendatestr[:4]), int(
            tokendatestr[4:6]), int(tokendatestr[6:8]))
        today = datetime.date.today()
        if(today != tokendate):
            raise Exception('Token date expired')
        kite = KiteConnect(api_key=getConfig(
            'api_key'), access_token= token)
        kws = KiteTicker(getConfig('api_key'), token)
        return kite, kws
