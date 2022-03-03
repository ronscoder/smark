import pandas as pd

def mva(window_size, data):
    return pd.Series(data).rolling(window=window_size).mean()