from binance.client import Client
from binance.enums import *
import time, config
from tools import *

class Asset:
    def __init__(self, symbol, q_precision):
        self.symbol = symbol
        self.baseAsset = info(self.symbol)['baseAsset']
        self.balance = get_balance(self.baseAsset)
        self.price = get_price(self.symbol)
        self.funds = funds()        
        self.q_precision = q_precision
        self.buy_price = get_buy_price(self.symbol)

    def update(self):
        self.price = get_price(self.symbol)
        self.balance = get_balance(self.baseAsset)
        self.buy_price = get_buy_price(self.symbol)
        self.funds = funds()
    
    def buy_quantity(self, price):        
        quant = self.funds/price
        return truncate_float(quant, self.q_precision)

    def sell_quantity(self):
        quant = self.balance
        return truncate_float(quant, self.q_precision)

def get_balance(asset):
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        raw = client.get_asset_balance(asset=asset)['free']
    except Exception as e:
        print(asset + " balance() exception occurred - {}".format(e))
        return False
    val = float(raw)        
    
    return val

def funds():
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        raw = client.get_asset_balance(asset='USDT')['free']
    except Exception as e:
        print('USDT' + " balance() exception occurred - {}".format(e))
        return False
    val = float(raw)        
    
    return truncate_float(val, 6)

def info(symbol):
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        raw = client.get_symbol_info(symbol=symbol)
    except Exception as e:
        print(symbol + " info() exception occurred - {}".format(e))
        time.sleep(.5)
        return False       
    
    return raw

def get_price(symbol):
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        price = client.get_avg_price(symbol=symbol)
    except Exception as e:
        print("price() exception occurred - {}".format(e))
        time.sleep(.5)
        return False
    return truncate_float(float(price['price']), 6)

def buy_quantity(funds, price):
    amount = float(funds/price)
    return truncate_float(amount, 6) 

def buy(symbol, quantity):
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    print(quantity)
    try:
        print("sending BUY order")
        order = client.create_order(symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=quantity, newOrderRespType='FULL')
    except Exception as e:
        print("BUY exception occured - {}".format(e))
        time.sleep(.5)
        return False
    print('Bought at: ', time.time())
    print(order)
    return order

def limit_buy(symbol, price, qty):
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        print("sending BUY order at: ", time.time())
        order = client.create_order(symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_LIMIT, timeInForce='GTC', quantity=qty, price=price)        
    except Exception as e:
        print("BUY exception occured - {}".format(e))
        time.sleep(.5)
        return False
    
    return order['orderId']

def sell(symbol, quantity):
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    print(quantity)
    try:
        print("sending SELL order")
        order = client.create_order(symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=quantity)
    except Exception as e:
        print("SELL exception occured - {}".format(e))
        time.sleep(.5)
        return False
    print(order)
    print("Sold at: ", time.time())
    return order

def limit_sell(symbol, price, qty):
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        print("sending SELL order at: ", time.time())
        order = client.create_order(
                    symbol=symbol, 
                    side=SIDE_SELL, 
                    type=ORDER_TYPE_LIMIT, 
                    timeInForce='GTC', 
                    quantity=qty, 
                    price=price
                    )
    except Exception as e:
        print("SELL exception occured - {}".format(e))
        time.sleep(.5)
        return False
    
    return order['orderId']

def cancel_order(symbol, orderId):
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        cancel = client.cancel_order(symbol=symbol, orderId=orderId)
        
    except Exception as e:
        print('CANCEL exception occured- {}'.format(e))
        time.sleep(.5)
    print(cancel)

def get_buy_price(symbol):
        client = Client(config.API_KEY, config.API_SECRET, tld='us')
        try:
            trade = client.get_my_trades(symbol= symbol, limit=1)[0]
        except Exception as e:
            print("BUY PRICE exception occurred - {}".format(e))
            return False
        if trade['isBuyer'] == True:
            return truncate_float(trade['price'], 4)
        else:
            return 0


