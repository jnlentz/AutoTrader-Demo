from assets import *
from binance.enums import *
from binance.client import Client
from tools import *
from data_manager import *
from time import *

#Contains core algorithm
class TradeHandler:
    
    def __init__(self, symbol, precision):
        self.df = None
        self.asset = Asset(symbol, precision)
        self.holding = False
        self.buying = False
        self.selling = False
        self.buy_timer = 0
        self.sell_timer = 0
        self.active_order = 0
    
    # Pulls initial dataset and checks starting trade position
    def setup(self):
        self.df = get_recent(self.asset.symbol, Client.KLINE_INTERVAL_3MINUTE, 120)
        self.asset.update() # Update balances for USDT and LTC
        return True

    #Core algorithm
    def spin(self):
        self.df = get_recent(self.asset.symbol, Client.KLINE_INTERVAL_3MINUTE, 100)
        self.asset.update() # Update balances for USDT and LTC
        currRSI = self.df['rsi'].iat[-1] # Current RSI value
        maRSI = self.df['rsi'].iloc[-3:-1].mean() # average of RSI over last 10 periods
        rsi_slope = slope(self.df.iloc[-3:-1]) # slope of RSI over last 10 periods
        mod = maRSI*rsi_slope # slope adjustment

        if self.holding == True:
            if self.selling == True:
                if self.asset.funds > 1:
                    self.holding = False
                    self.selling = False
                    self.active_order = 0
                    print('Sell order filled at: ', time())
                    print('===================================')
                    return False  
            else:
                self.sell_timer += 1
                if self.sell_timer > 25:
                    cancel_order(self.asset.symbol, self.active_order)
                    sell(self.asset.symbol, self.asset.sell_quantity())
                    self.holding = False
                    self.selling = False
                    self.active_order = 0
                    self.sell_timer = 0
                    print('Force sell at: ', time())
                    print('===================================')
                    return False

        else:   
            if self.asset.balance > .01:
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
            elif self.buying == True:
                self.buy_timer+=1
                if self.buy_timer > 1:
                    self.buying = False
                    cancel_order(self.asset.symbol, self.active_order)
                    self.buy_timer = 0
                    return True
            elif currRSI < maRSI-(mod-5):
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
    

    

    
             
            
    