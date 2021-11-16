from assets import *
from binance.enums import *
from binance.client import Client
from tools import *
from time import *

#Contains core algorithm
class TradeHandler:
    
    def __init__(self, symbol, precision, pos_size):
        self.df = None # Data currently in use, updated every cycle
        self.asset = Asset(symbol, precision, pos_size) # Contains methods for buying, selling, and retrieving pertinent account information

        # Algorithm variables
        self.holding = False # True when holding assets to be sold
        self.buying = False # True when a buy order is ready to be placed
        self.selling = False # True when a sell order is ready to be placed
        self.buy_timer = 0
        self.sell_timer = 0
        self.active_order = 0 # OrderID of currently pending order
    
    # Pulls initial dataset and checks starting trade position
    def setup(self):
        self.df = get_recent(self.asset.symbol, Client.KLINE_INTERVAL_3MINUTE, 120)
        self.asset.update() 
        return True

    #Core algorithm
    def trade(self):
        self.df = get_recent(self.asset.symbol, Client.KLINE_INTERVAL_3MINUTE, 100) # Update dataset
        self.asset.update() # Update balances for USDT and LTC
        currRSI = self.df['rsi'].iat[-1] # Current RSI value
        maRSI = self.df['rsi'].iloc[-3:-1].mean() # average of RSI over last 10 periods
        rsi_slope = slope(self.df.iloc[-3:-1]) # slope of RSI over last 10 periods
        mod = maRSI*rsi_slope # slope adjustment

        if self.holding == True: 
            if self.selling == True: 
                if self.asset.funds > 1: # Sell order filled, reset for next buy
                    self.holding = False
                    self.selling = False
                    self.active_order = 0
                    print('Sell order filled at: ', time())
                    print('===================================')
                    return False  
            else: 
                self.sell_timer += 1
                if self.sell_timer > 25: # If sell order unfilled for more than 25 cycles, sell at current price and reset for next buy
                    cancel_order(self.asset.symbol, self.active_order)
                    sell(self.asset.symbol, self.asset.sell_quantity())
                    self.holding = False
                    self.selling = False
                    self.active_order = 0
                    self.sell_timer = 0
                    print('Force sell at: ', time())
                    print('===================================')
                    return False

        else:  #
            if self.asset.balance > .0001: # Buy order filled, place sell order
                self.holding = True
                self.buying = False
                print('Buy order filled at: ', time())
                print('++++++++++++++++++++++++++++++++++') 
                target_price = truncate_float(self.asset.buy_price*1.005, 2)
                sale = limit_sell(self.asset.symbol, target_price, self.asset.sell_quantity())                    
                if sale == False:
                    return True
                else:
                    print('===================================')
                    print('Sell order placed at: ', time())
                    print('Target price: ', target_price)
                    self.active_order = sale
                    self.selling = True
                    return False              
            elif self.buying == True: # If buy order unfilled for more than 2 cycles, cancel and reset
                self.buy_timer+=1
                if self.buy_timer > 1:
                    self.buying = False
                    cancel_order(self.asset.symbol, self.active_order)
                    self.buy_timer = 0
                    return True
            elif currRSI < maRSI-(mod-5): # If RSI is lower than expected place an order for an even lower price
                target_price = truncate_float(self.asset.price*.996, 2)  
                print('++++++++++++++++++++++++++++++++++')            
                purchase = limit_buy(self.asset.symbol, target_price, self.asset.buy_quantity(target_price))
                if purchase == False:
                    return True
                else:
                    self.buying = True
                    self.active_order = purchase
                    print('Buy order placed at: ', time())
                    print('Target price: ', target_price)
            return False
    

    

    
             
            
    