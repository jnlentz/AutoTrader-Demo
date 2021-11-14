import numpy as np
import pandas as pd
from binance.client import Client
from binance.enums import *
import config, time
# ------------------- Data formatting ---------------------
def format_kline(row):
        time = round(float(row[0])/1000)
        open = float(row[1])
        high = float(row[2])
        low = float(row[3])
        close = float(row[4])       
        volume = float(row[5])
        if open > close:
            volume = 0 - volume
        change = close-open
        perc_change = change/open 
        out = [time, open, high, low, close, volume, perc_change]
        return out

def format_trade(row):    
    time = round(float(row['time'])/1000)
    id = row['orderId']
    symbol = row['symbol']
    price = row['price']
    qty = row['qty']
    quoteQty = row['quoteQty']
    buyer = row['isBuyer']
    out = [time, id, symbol, price, qty, quoteQty, buyer]
    return out
    
def format_order(row):
    time = round(float(row['time'])/1000)
    id = row['orderId']
    symbol = row['symbol']
    price = float(row['price'])
    qty = float(row['origQty'])
    quoteQty = float(row['cummulativeQuoteQty'])
    exQty = float(row['executedQty'])
    status = row['status']
    side = row['side']

    out = [time, id, symbol, price, qty, quoteQty, exQty, status, side]
    return out

def truncate_float(n, precision):
        s = str(n)
        dp = s.find('.')+1
        out = s[0:dp+precision]
        return float(out)

# ------------------- Data collection ---------------------

def get_any(symbol, interval, start, end):
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        target = client.get_historical_klines(symbol, interval, start, end)
    except Exception as e:
        print("GET exception occurred - {}".format(e))
        return False
    rows = []
    for row in target:
        rows.append(format_kline(row))
    df = pd.DataFrame(rows, columns=['time','open','high','low', 'close', 'volume', 'perc_change'])
    df['total_volume'] = df['volume'].rolling(10).sum()
    df['total_perc_change'] = df['perc_change'].rolling(10).sum()
    df['rsi'] = computeRSI(df['close'], 14)
    df['ema7'] = df['close'].ewm(span=7).mean()
    df['ema25'] = df['close'].ewm(span=25).mean()
    df['ema99'] = df['close'].ewm(span=99).mean()

    return df

def get_recent(symbol, interval, limit):
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        kline = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    except Exception as e:
        print("GET exception occurred - {}".format(e))
        time.sleep(2)
        return get_recent(symbol, interval, limit)

    rows = []
    for row in kline:
        rows.append(format_kline(row))
    df = pd.DataFrame(rows, columns=['time','open','high','low', 'close', 'volume', 'perc_change'])
    df['total_volume'] = df['volume'].rolling(10).sum()
    df['total_perc_change'] = df['perc_change'].rolling(10).sum()
    df['rsi'] = computeRSI(df['close'], 14)
    df['ema7'] = df['close'].ewm(span=7).mean()
    df['ema25'] = df['close'].ewm(span=25).mean()
    df['ema99'] = df['close'].ewm(span=99).mean()
    return df




# ------------------- Data processing ---------------------
def computeRSI (data, time_window):
    diff = data.diff(1).dropna()        # diff in one field(one day)

    #this preservers dimensions off diff values
    up_chg = 0 * diff
    down_chg = 0 * diff
    
    # up change is equal to the positive difference, otherwise equal to zero
    up_chg[diff > 0] = diff[ diff>0 ]
    
    # down change is equal to negative deifference, otherwise equal to zero
    down_chg[diff < 0] = diff[ diff < 0 ]
    
    up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    
    rs = abs(up_chg_avg/down_chg_avg)
    rsi = 100 - 100/(1+rs)
    return rsi
    
def slope(data):
        df = data
        x = df.index
        y = df['rsi']
        m, b = np.polyfit(x, y, 1)
        return m

