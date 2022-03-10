import datetime
import webbrowser
from kiteconnect import KiteConnect
from libs.configs import getConfig, setConfig
# from boto.s3.connection import S3Connection
import os

def get_new_token(request_token=None):
    kite = KiteConnect(api_key=getConfig('api_key'))
    now = datetime.datetime.now()
    print(kite.login_url())
    if(request_token is None):
        print("Open")
        # print(kite.login_url())
        webbrowser.open(kite.login_url(), new=0, autoraise=True)
        request_token = input('Enter request token: ')
        if (request_token == ''):
            exit()
    try:
        data = kite.generate_session(request_token, api_secret=getConfig('api_secret'))
        # print(data)
        access_token = data['access_token']
        val = f'{now.year}{now.month:02}{now.day:02}:{access_token}'
        setConfig('ACCESS_TOKEN', val)
        print('new access token', val)
        # os.environ['ACCESS_TOKEN'] = val
        return access_token
    except Exception as ex: 
        print('ERROR getting new access token', ex.__str__())
        return None


def get_access_token():
    # print('ACCESS_TOKEN')
    access_token = getConfig('ACCESS_TOKEN')
    # access_token = os.environ.get('ACCESS_TOKEN', None)
    # print(access_token)
    if(access_token is None):
        print('No access token')
        return
    tokendatestr, token = access_token.split(":")
    tokendate = datetime.date(int(tokendatestr[:4]), int(
        tokendatestr[4:6]), int(tokendatestr[6:8]))
    today = datetime.date.today()
    if(today != tokendate):
        print('Access token expired.')
        return
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
    print(get_new_token())