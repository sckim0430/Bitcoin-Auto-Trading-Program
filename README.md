# Upbit Auto Trading Program
   
<p align="left"><img src="https://user-images.githubusercontent.com/63839581/118985117-24a7d800-b9b9-11eb-9e72-64f148bc72d0.jpg" width="600"></p>   
   
## Description
   
This repository was implemented under the theme of **Upbit Won Market Automatic Trading Program**, a cryptocurrency exchange.
   
## Installation
   
Requires Python 3.6 or higher version. [Anaconda] (https://www.anaconda.com/) installation is recommended.  
This repository is based on the API provided by [PyUpbit] (https://github.com/sharebook-kr/pyupbit). Please familiarize yourself with the basic API in the relevant repository.
   
intall pyupbit, pyjwt

```bash
$ pip install pyupbit
```   
   
```bash
$ pip install pyjwt
```   
   
## Start

Before starting, get an access key and secret key from Upbit's API support section, and write the following part in [auto_trading.py](https://github.com/sckim0430/Upbit-Auto-Trading-Program/blob/master/auto_trading.py).
   
```bash
access = ''
secret = ''
```   
   
After modifying the parameters in [auto_trading.py](https://github.com/sckim0430/Upbit-Auto-Trading-Program/blob/master/auto_trading.py), run the program.
   
```bash
python auto_trading.py
```   

Codes related to buying can be viewed in [upbitbot_buy_module.py](https://github.com/sckim0430/Upbit-Auto-Trading-Program/blob/master/upbitbot_buy_module.py), and codes related to selling can be viewed in [upbitbot_sell_module.py ](https://github.com/sckim0430/Upbit-Auto-Trading-Program/blob/master/upbitbot_sell_module.py).

By implementing **multi-processing**, you can selectively use the buy and sell functions. Just edit the following part in [auto_trading.py](https://github.com/sckim0430/Upbit-Auto-Trading-Program/blob/master/auto_trading.py).
   
```bash
buy_process = multiprocessing.Process(target=buy_worker,args=('upbitbot_buy_module.py',FEE,MIN_ORDER_PRICE,BUY_STACK
        ,SLEEP_TIME,CHECK_TIME,DAY_CHECK_TIME,MAX_COIN_COUNT,markets,market_count,day_markets))

sell_process = multiprocessing.Process(target=sell_worker,args=('upbitbot_sell_module.py',SLEEP_TIME,CHECK_TIME_SELL,markets,market_count,SELL_MIN_VAL,SELL_STACK))
        
buy_process.start()
sell_process.start()
        
buy_process.join()
sell_process.join()
```    

## Warning
   
Please take note of the following precautions.
   
1. The code is dedicated to the KRW market (KRW).   
   
2. Please refrain from using the program when information on the market has changed (delisting, new listing, etc.) or when checking Upbit.
   
3. The rate of return may vary depending on market conditions, so please test it thoroughly before using it.
   
4. At the beginning of the program, if you do not place a limit order among already purchased coins, please note that they may be sold immediately by the sell program. 
   
## Contact
   
another0430@naver.com
