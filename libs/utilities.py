import yfinance as yf
import datetime

def ydownload(symbol, startdate, enddate=None, interval='5m'):
    if(enddate==None):
        enddate = datetime.datetime.today().date()
    return yf.download(symbol, start=f'{startdate.year}-{startdate.month:02}-{startdate.day:02}', end=f'{enddate.year}-{enddate.month:02}-{enddate.day+1:02}', interval=interval)

def is_holiday(date: datetime.date):
    day = date.weekday()
    if(day in [5, 6]):
        return True
    from libs.configs import getConfig
    holidays = getConfig('holidays')
    date_string = f'{date.year}{date.month:02}{date.day:02}'
    if(date_string in holidays):
        return True
    return False



def get_last_working_day(from_date = None, days_offset=1):
    if(from_date == None):
        from_date = datetime.datetime.today().date()
    lastworkingday = from_date - datetime.timedelta(days=days_offset)
    while(is_holiday(lastworkingday)):
        lastworkingday = lastworkingday - datetime.timedelta(days=1)
    return lastworkingday
