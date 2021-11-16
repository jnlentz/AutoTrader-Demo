# Overview
AutoTrader is a bot designed for algorithmic trading on the Binance cryptocurrency exchange. It is meant to reliably excecute a trading algorithm (or algorithms) at user defined time intervals.  Based on live testing results, the algorithm currently contained in the TradeHandler class will very probably **lose** over time.  It is included only for demonstration purposes.  The code is written to allow the algorithm to be changed with minimal concerns about reliability.  

## Setup 
**Dependent libraries:** Dash, python-binance, pandas, numpy

**Enter your Binance API keys into their respective fields in the 'config' file.** 

**main.py** 
Modify the inputs to the TradeHandler() constructor on line 12 to whatever trading pair you want to trade.  The second argument is the precision that quantaties of that asset need to be rounded to when placing orders.  The third is the percentage of your available USD funds you want to trade - 1 is 100%.  

To change the time interval, alter the 'interval' value on line 26.  Time is expressed in milliseconds.

**trade_handler.py**
The trade() function houses the algorithm and is called at each interval.  Alter this function to buy and sell according to your conditions.  