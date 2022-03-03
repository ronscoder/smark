import yfinance as yf


def ydownload(symbol, startdate, enddate, interval='5m'):
    return yf.download(symbol, start=startdate,
                                    end=enddate, interval=interval)