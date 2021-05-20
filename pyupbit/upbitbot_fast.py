import pyupbit as pu
import time
import numpy as np
import sys

#buy_markets에 있는 코인이 상장 폐지된 경우 직접 디지털 출금 주소 생성 후 출금

def get_start_buy_markets(upbit):  
    buy_markets = []

    for coin in upbit.get_balances():
        if coin['currency']=='KRW':
            continue

        if float(coin['balance']) == 0.0:
            continue
        
        buy_markets.append('KRW-'+coin['currency'])

    return buy_markets

def get_total_balance(upbit):
    balance_f = 0.0

    for balance in upbit.get_balances():
        if balance['currency']=='KRW':
            balance_f+=float(balance['balance'])
        else:
            balance_f+=((float(balance['balance'])*float(balance['avg_buy_price'])))
    
    return balance_f

def main():
    try:
        #초기화
        print('Setting Parameters!')

        FEE = 0.9995
        BUY_STACK = 2.5
        BUY_HIGH_TO_CURRENCT = 15
        SELL_MAX_VAL = 1.25   #최대 판매가 %
        SLEEP_TIME = 0.15
        MIN_ORDER_PRICE = 5000
        CHECK_TIME = 180            #3분
        DAY_CHECK_TIME = 10800       #1시간
        MAX_COIN_COUNT = 5
                
        access = 'HxvWmdIoJao6HALepLk38S8EJPvqDKbAtYm6oQna'  # home
        secret = '1sHpwZV75yZRwhwCiW7ZeZ86c78LqovscXXQgD1V'  # home

        # access = 'j1oiF6zi0kM2WTtVAbYgXuTs84zyd5xnh2dba2D1'     # company
        # secret = 'dIB6cqG1StOLxZv3lJxt30JRGYjy4A5WnhrY8LyV'     # company

        upbit = pu.Upbit(access,secret)
        
        markets = pu.get_tickers(fiat="KRW")
        market_count = len(markets)

        stack_markets = np.zeros(market_count)
        stack_markets_order = np.zeros(market_count)
        stack_markets_order_index = np.zeros(market_count)
            
        buy_markets = get_start_buy_markets(upbit)

        balance_f = get_total_balance(upbit)
        
        time_stack_check = 0.0
        time_day_check = 0.0

        maximum_markets = []
        day_markets = []

        for market in markets:
            maximum_markets.append(max(pu.get_ohlcv(market,interval="month",count=3)['high']))
            time.sleep(SLEEP_TIME)

            day_info = pu.get_ohlcv(market,interval='day',count=13)['close']
            time.sleep(SLEEP_TIME)
            ten_day_line = np.asarray(list(day_info.rolling(10).mean()[-3:]))
            five_day_line = np.asarray(list(day_info.rolling(5).mean()[-3:]))

            day_markets.append((five_day_line>ten_day_line).min())

        print('start with {}'.format(buy_markets))
        print('start balance : {}'.format(balance_f))

        #가격 변동 파악-1
        prices = np.asarray(list(pu.get_current_price(markets[:100]).values()))
        prices = np.hstack((prices,list(pu.get_current_price(markets[100:]).values())))
        time_first = time.time()

        while True:
            #마켓 변동 사항 파악
            new_markets = pu.get_tickers(fiat="KRW")

            if market_count != len(new_markets):

                markets = new_markets
                market_count = len(markets)
                stack_markets = np.zeros(market_count)
                stack_markets_order = np.zeros(market_count)
                stack_markets_order_index = np.zeros(market_count)
                time_stack_check = 0.0
                time_day_check = 0.0

                maximum_markets.clear()
                day_markets.clear()

                for market in markets:
                    maximum_markets.append(max(pu.get_ohlcv(market,interval="month",count=3)['high']))
                    time.sleep(SLEEP_TIME)

                    day_info = pu.get_ohlcv(market,interval='day',count=13)['close']
                    time.sleep(SLEEP_TIME)
                    ten_day_line = np.asarray(list(day_info.rolling(10).mean()[-3:]))
                    five_day_line = np.asarray(list(day_info.rolling(5).mean()[-3:]))

                    day_markets.append((five_day_line>ten_day_line).min())

            #구매
            positive_price = upbit.get_balance("KRW")
            time.sleep(SLEEP_TIME)

            if positive_price>=MIN_ORDER_PRICE * (1/FEE) and not (stack_markets_order == np.zeros(market_count)).min():
                for index,s in enumerate(stack_markets_order):
                    if len(buy_markets)>=MAX_COIN_COUNT:
                        break

                    if day_markets[stack_markets_order_index[index]] and (s >= BUY_STACK) and (markets[stack_markets_order_index[index]] not in buy_markets):                
                        
                        positive_price = upbit.get_balance("KRW")
                        time.sleep(SLEEP_TIME)

                        if positive_price>=MIN_ORDER_PRICE * (1/FEE):
                            time_info = pu.get_ohlcv(markets[stack_markets_order_index[index]],interval='minute1',count=23)['close']
                            time.sleep(SLEEP_TIME)

                            current_price = time_info[-1]
                            ten_time_line = np.asarray(list(time_info.rolling(10).mean()[-3:]))
                            twenty_time_line = np.asarray(list(time_info.rolling(20).mean()[-3:]))

                            if (ten_time_line>twenty_time_line).min() and ((maximum_markets[stack_markets_order_index[index]]-current_price)/maximum_markets[stack_markets_order_index[index]])*100>= BUY_HIGH_TO_CURRENCT: 
                                BUY_BALANCE = get_total_balance(upbit)/MAX_COIN_COUNT
                                order_price = BUY_BALANCE*FEE
                                
                                if order_price>= positive_price:
                                    order_price = positive_price*FEE

                                upbit.buy_market_order(markets[stack_markets_order_index[index]],order_price)
                                time.sleep(SLEEP_TIME)
                                buy_markets.append(markets[stack_markets_order_index[index]])
                                print('buy : {}, markets : {}, order_price : {}'.format(markets[stack_markets_order_index[index]],buy_markets,order_price))
                        else:
                            break


            #판매
            delete_market_list = []
            total_balance = upbit.get_balances()
            time.sleep(SLEEP_TIME)

            for index,b_m in enumerate(buy_markets):
                for bal_info in total_balance:
                    if 'KRW-'+bal_info['currency'] == b_m:
                        avg_buy_price = float(bal_info['avg_buy_price'])
                        balance = bal_info['balance']

                        if avg_buy_price == 0.0:
                            print('error average buy price of {}'.format(b_m))
                            break
                        
                        current_price = pu.get_current_price(b_m)
                        time.sleep(SLEEP_TIME)
                        change_val_avg =((current_price - avg_buy_price)/ avg_buy_price)* 100

                        if (change_val_avg>= SELL_MAX_VAL):
                            upbit.sell_market_order(b_m,balance)
                            time.sleep(SLEEP_TIME)
                            delete_market_list.append(b_m)
                        break

            for _ in delete_market_list:
                buy_markets.remove(_)
                print('sell : {}, markets : {}'.format(_,buy_markets))
            
            #가격 변동 파라미터 초기화
            if time_stack_check >= CHECK_TIME:
                time_stack_check = 0.0
                stack_markets = np.zeros(market_count)
                stack_markets_order = np.zeros(market_count)
                stack_markets_order_index = np.zeros(market_count)

            #최고가 및 마켓 각 코인의 상승장 여부 파악
            if time_day_check >= DAY_CHECK_TIME:
                time_day_check = 0.0
                
                maximum_markets.clear()
                day_markets.clear()

                for market in markets:
                    maximum_markets.append(max(pu.get_ohlcv(market,interval="month",count=3)['high']))
                    time.sleep(SLEEP_TIME)

                    day_info = pu.get_ohlcv(market,interval='day',count=13)['close']
                    time.sleep(SLEEP_TIME)
                    ten_day_line = np.asarray(list(day_info.rolling(10).mean()[-3:]))
                    five_day_line = np.asarray(list(day_info.rolling(20).mean()[-3:]))

                    day_markets.append((five_day_line>ten_day_line).min())


            #가격 변동 파악-2
            prices_now = np.asarray(list(pu.get_current_price(markets[:100]).values()))
            prices_now = np.hstack((prices_now,list(pu.get_current_price(markets[100:]).values())))
            time_last = time.time()

            change_val = ((prices_now-prices)/prices)*100
            prices = prices_now

            stack_markets += change_val
            stack_markets_order = np.sort(stack_markets)[::-1]
            stack_markets_order_index = (-stack_markets).argsort()
            
            time_stack_check += (time_last - time_first)
            time_day_check += (time_last - time_first)

            time_first = time_last

    except KeyboardInterrupt:
        print('start balance : {}, last balance : {}'.format(balance_f,get_total_balance(upbit)))
        print('exit the program!')
        sys.exit()

if __name__ == "__main__":
        main()        