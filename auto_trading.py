"""Upbit Auto Trading System
"""
import multiprocessing
from os import system
import sys
import pyupbit as pu
import time
import numpy as np

##########################################################################################################
#markets 정보가 바뀐 경우 새로 실행(market이 새로 추가된 경우, 상장 폐지된 경우)
#buy_markets에 있는 코인이 상장 폐지된 경우 직접 디지털 출금 주소 생성 후 출금
#업비트 거래소 점검 시 프로그램 직접 종료 후 점검 완료 후 다시 실행
##########################################################################################################
access = ''     # access key
secret = ''     # secret key
upbit = pu.Upbit(access, secret)
##########################################################################################################


def get_buy_markets():
    """Returns a List of Coins Already Ordered or Purchased

    Returns:
        list, list: Already Purchased Coin List, Ordered Coin List
    """
    buy_markets = []
    ordered_markets = []

    for coin in upbit.get_balances():
        if coin['currency'] == 'KRW' or coin['currency'] == 'USDT':
            continue

        if float(coin['balance']) == 0.0:
            ordered_markets.append('KRW-'+coin['currency'])
            continue

        buy_markets.append('KRW-'+coin['currency'])

    return buy_markets, ordered_markets


def get_total_balance():
    """Returns Total Assets

    Returns:
        float: Total Asset
    """
    balance_f = 0.0

    for balance in upbit.get_balances():
        if balance['currency'] == 'KRW':
            balance_f += float(balance['balance'])
        else:
            balance_f += ((float(balance['balance'])
                          * float(balance['avg_buy_price'])))

    return balance_f


def get_balance(key):
    """Returns A Certain Amount of Coins or Amount Available to Order

    Args:
        key (str): "Coin Name" or "KRW"

    Returns:
        float: Amount Coin or Amount Available to Order
    """
    return upbit.get_balance(key)


def get_balances():
    """Returns Total Assets with (Amount of Coin, Amount Avaliable to Order)

    Returns:
        dict: Amount of Coin, Amount Avaliable to Order
    """
    return upbit.get_balances()


def get_sell_val(price):
    """Returns Sell Price Unit

    Args:
        price (float): coin price

    Returns:
        float: Sell Price Unit
    """
    price = float(price)

    if price >= 2000000:
        sell_val = (1000/price) * 100
    elif price >= 1000000:
        sell_val = (500/price) * 100
    elif price >= 500000:
        sell_val = (100/price) * 100
    elif price >= 100000:
        sell_val = (50/price) * 100
    elif price >= 10000:
        sell_val = (10/price) * 100
    elif price >= 1000:
        sell_val = (5/price) * 100
    elif price >= 100:
        sell_val = (1/price) * 100
    elif price >= 10:
        sell_val = (0.1/price) * 100
    else:
        sell_val = (0.01/price) * 100

    return sell_val


def buy_market_order(market, price):
    """Buy Coin

    Args:
        market (str): coin name to buy
        price (float): price to buy
    """
    upbit.buy_market_order(market, price)


def sell_market_order(market, balance):
    """Sell Coin

    Args:
        market (str): coin name to buy
        balance (float): price to buy
    """
    upbit.sell_market_order(market, balance)


def buy_worker(file, FEE, MIN_ORDER_PRICE, BUY_STACK, SLEEP_TIME, CHECK_TIME, DAY_CHECK_TIME,
               MAX_COIN_COUNT, markets, market_count, day_markets):
    """Buy Module

    Args:
        file (str): buy module file path
        FEE (float): ㅊommission
        MIN_ORDER_PRICE (int): min order price
        BUY_STACK (float): buy module parameter
        SLEEP_TIME (float): delay time
        CHECK_TIME (int): time to check the amount of change
        DAY_CHECK_TIME (int): time to check the amount of coin price change
        MAX_COIN_COUNT (int): max coin number
        markets (list): already have coin list
        market_count (int): total coin number in market
        day_markets (list): target coin list
    """
    try:
        markets = str(markets).replace(" ", "")
        day_markets = str(day_markets).replace(" ", "")

        system('python {} {} {} {} {} {} {} {} {} {} {}'.format(file, FEE, MIN_ORDER_PRICE, BUY_STACK,
               SLEEP_TIME, CHECK_TIME, DAY_CHECK_TIME, MAX_COIN_COUNT, markets, market_count, day_markets))
    except:
        print('Buy Moudle have Error!!')


def sell_worker(file, SLEEP_TIME, CHECK_TIME_SELL, markets, market_count, SELL_MIN_VAL, SELL_STACK):
    """Sell Module

    Args:
        file (str): sell module file path
        SLEEP_TIME (float): delay time
        CHECK_TIME_SELL (int): time to check the amount of change
        markets (list): already have coin list
        market_count (int): total coin number in market
        SELL_MIN_VAL (float): percent of price to sell
        SELL_STACK (float): sell module parameter
    """
    try:
        markets = str(markets).replace(" ", "")
        system('python {} {} {} {} {} {} {}'.format(file, SLEEP_TIME,
               CHECK_TIME_SELL, markets, market_count, SELL_MIN_VAL, SELL_STACK))
    except:
        print('Sell Moudle have Error!!')


def main():
    try:
        #####################################################초기화#####################################################
        print('Setting Parameters!')
        FEE = 0.9995
        MIN_ORDER_PRICE = 5000
        BUY_STACK = 1.25
        SELL_STACK = -2.25
        # BUY_HIGH_TO_CURRENCT = 10
        SELL_MIN_VAL = 1.25  # 판매가 %

        SLEEP_TIME = 0.16
        CHECK_TIME = 180  # 3분
        CHECK_TIME_SELL = 60  # 1분
        DAY_CHECK_TIME = 43200  # 12시간

        MAX_COIN_COUNT = 5

        markets = pu.get_tickers(fiat="KRW")
        market_count = len(markets)

        balance_f = get_total_balance()

        day_markets = []

        for market in markets:
            day_info = pu.get_ohlcv(market, interval='day', count=13)['close']
            time.sleep(SLEEP_TIME)
            ten_day_line = np.asarray(list(day_info.rolling(10).mean()[-3:]))
            five_day_line = np.asarray(list(day_info.rolling(5).mean()[-3:]))

            day_markets.append((five_day_line > ten_day_line).min())

        buy_markets, _ = get_buy_markets()

        print('start with {}'.format(buy_markets))
        print('start balance : {}'.format(balance_f))

        #####################################################실행#####################################################
        buy_process = multiprocessing.Process(target=buy_worker, args=('upbitbot_buy_module.py', FEE, MIN_ORDER_PRICE,
                                              BUY_STACK, SLEEP_TIME, CHECK_TIME, DAY_CHECK_TIME, MAX_COIN_COUNT, markets, market_count, day_markets))

        sell_process = multiprocessing.Process(target=sell_worker, args=(
            'upbitbot_sell_module.py', SLEEP_TIME, CHECK_TIME_SELL, markets, market_count, SELL_MIN_VAL, SELL_STACK))

        buy_process.start()
        sell_process.start()

        buy_process.join()
        sell_process.join()

    except:
        print('start balance : {}, last balance : {}'.format(
            balance_f, get_total_balance()))
        print('exit the program!')
        sys.exit()


if __name__ == "__main__":
    main()
