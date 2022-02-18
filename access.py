import datetime
import os
import webbrowser
from kiteconnect import KiteConnect
from libs.configs import getConfig, setConfig

def get_new_token():
    kite = KiteConnect(api_key=getConfig('api_key'))
    now = datetime.now()
    print("Open")
    print(kite.login_url())
    webbrowser.open(kite.login_url(), new=0, autoraise=True)
    request_token = input('Enter request token: ')
    if (request_token == ''):
        exit()
    data = kite.generate_session(request_token, api_secret=getConfig('api_secret'))
    print(data)
    access_token = data['access_token']
    val = f'{now.year}{now.month:02}{now.day:02}:{access_token}'
    setConfig('ACCESS_TOKEN', val)
    return access_token

def get_access_token():
    print('ACCESS_TOKEN')
    access_token = getConfig('ACCESS_TOKEN')
    print(access_token)
    if(access_token is None):
        return get_new_token()
    tokendatestr, token = access_token.split(":")
    tokendate = datetime.date(int(tokendatestr[:4]), int(
        tokendatestr[4:6]), int(tokendatestr[6:8]))
    today = datetime.date.today()
    if(today != tokendate):
        return get_new_token()
    return token


# def run_access():
#     kite = KiteConnect(api_key=getConfig('api_key'))
#     access_token = get_access_token(kite)
#     now = datetime.now()
#     print()
#     val = f'{now.year}{now.month:02}{now.day:02}:{access_token}'
#     setConfig('ACCESS_TOKEN', val)
#     print()

if __name__ == "__main__":
    print(get_access_token())