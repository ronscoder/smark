import datetime
import webbrowser
from kiteconnect import KiteConnect
from libs.configs import getAccessToken, getRequestToken, setAccessToken
import subprocess
# from boto.s3.connection import S3Connection
import os

def get_new_token(request_token=None):
    # api_key = getConfig('api_key')
    api_key = '7zx0e8g535qgefu6'
    # api_secret = getConfig('api_secret')
    api_secret = 'utwyn9ugmbxfcx6wurcd869mtvn2ck30'
    kite = KiteConnect(api_key=api_key)
    now = datetime.datetime.now()
    print(kite.login_url())
    if(request_token is None):
        print("Open")
        # print(kite.login_url())
        webbrowser.open(kite.login_url(), new=0, autoraise=True)
        request_token = input('Ennter request token: ')
        if (request_token == ''):
            exit()
    try:
        # import pdb
        # pdb.set_trace()
        data = kite.generate_session(request_token, api_secret=api_secret)
        # print(data)
        access_token = data['access_token']
        val = f'{now.year}{now.month:02}{now.day:02}:{access_token}'
        print('new access token', val)
        setAccessToken(val)
        # print('os.environ', os.environ)
        if('ON_HEROKU' in os.environ):
            os.environ['ACCESS_TOKEN'] = val
            # subprocess.run(["heroku", "config:set", f"ACCESS_TOKEN={access_token}"])
        # os.environ['ACCESS_TOKEN'] = val
        return access_token
    except Exception as ex: 
        print('ERROR getting new access token', ex.__str__())
        return None


def get_access_token():
    # print('ACCESS_TOKEN')
    access_token = getAccessToken()
    # access_token = os.environ.get('ACCESS_TOKEN', None)
    # print(access_token)
    if(access_token is None):
        request_token = getRequestToken()
        print('request_token', request_token)
        print('No access token. Getting new')
        access_token = get_new_token(request_token)
    if(access_token is None):
        print('Error getting access token')
        return
    print('access_token', access_token)
    tokendatestr, token = access_token.split(":")
    tokendate = datetime.date(int(tokendatestr[:4]), int(
        tokendatestr[4:6]), int(tokendatestr[6:8]))
    today = datetime.date.today()
    if(today != tokendate):
        print('Access token expired.')
        request_token = getRequestToken()
        print('request_token', request_token)
        access_token = get_new_token(request_token)
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
    # print(get_new_token())
    get_access_token()