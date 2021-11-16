from binance.client import Client
from binance.enums import *
import time, config
from tools import *

class Asset:
    def __init__(self, symbol, q_precision, pos_size):
        self.symbol = symbol # Tradinhg pair tickers
        self.asset_symbol = info(self.symbol)['baseAsset'] # Target asset ticker
        self.balance = get_balance(self.asset_symbol) # Target asset balance
        self.price = get_price(self.symbol) # Current price 
        self.pos_size = pos_size # Percentage of total USD balance to trade
        self.funds = funds()*pos_size # USD balance to trade      
        self.q_precision = q_precision # Buy order quantities must be truncated to this precision to be accepted by the server
        self.buy_price = get_buy_price(self.symbol) # Price from last buy order
        

    def update(self): # Updates price and balance info each cycle
        self.price = get_price(self.symbol)
        self.balance = get_balance(self.asset_symbol)
        self.buy_price = get_buy_price(self.symbol)
        self.funds = funds()*self.pos_size
    
    def buy_quantity(self, price): # Calculates amount to be bought and truncates to precision  
        quant = self.funds/price
        return truncate_float(quant, self.q_precision)

    def sell_quantity(self): # Calculates amount to be sold and truncates to precision  
        quant = self.balance
        return truncate_float(quant, self.q_precision)

def get_balance(asset): # Current balance for target asset
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        raw = client.get_asset_balance(asset=asset)['free']
    except Exception as e:
        print(asset + " balance() exception occurred - {}".format(e))
        return False
    val = float(raw)        
    
    return val

def funds(): # Current USD balance
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        raw = client.get_asset_balance(asset='USDT')['free']
    except Exception as e:
        print('USDT' + " balance() exception occurred - {}".format(e))
        return False
    val = float(raw)        
    
    return truncate_float(val, 6)

def info(symbol): # Retrieve metadata for current trading pair - needed for q_precision
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        raw = client.get_symbol_info(symbol=symbol)
    except Exception as e:
        print(symbol + " info() exception occurred - {}".format(e))
        return False       
    
    return raw

def get_price(symbol): # Current price for target asset
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        price = client.get_avg_price(symbol=symbol)
    except Exception as e:
        print("price() exception occurred - {}".format(e))
        time.sleep(.5)
        return False
    return truncate_float(float(price['price']), 6)


def buy(symbol, quantity): # Market buy, takes whatever price is available
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

def limit_buy(symbol, price, qty): # Place an order to buy at a specific price
    client = Client(config.API_KEY, config.API_SECRET, tld='us')
    try:
        print("sending BUY order at: ", time.time())
        order = client.create_order(symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_LIMIT, timeInForce='GTC', quantity=qty, price=price)        
    except Exception as e:
        print("BUY exception occured - {}".format(e))
        time.sleep(.5)
        return False
    
    return order['orderId']

def sell(symbol, quantity): # Market sell, takes whatever price is available
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

def limit_sell(symbol, price, qty): # Place an order to buy at a specific price
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

def get_buy_price(symbol): # Retrieve price from last buy order
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


