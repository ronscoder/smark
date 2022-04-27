import yfinance as yf
import datetime

def ydownload(symbol, startdate, enddate, interval='5m'):
    return yf.download(symbol, start=startdate,
                                    end=enddate, interval=interval)

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



def get_last_working_day(from_date = None):
    if(from_date == None):
        from_date = datetime.datetime.today().date()
    lastworkingday = from_date - datetime.timedelta(days=1)
    while(is_holiday(lastworkingday)):
        lastworkingday = lastworkingday - datetime.timedelta(days=1)
    return lastworkingday
