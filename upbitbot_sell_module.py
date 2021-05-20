import pyupbit as pu
import time
import sys
from auto_trading import get_buy_markets,get_balances,sell_market_order,get_sell_val
import ast
import numpy as np

def main(SLEEP_TIME,CHECK_TIME_SELL,markets,market_count,SELL_MIN_VAL,SELL_STACK):
    try:
        stack_markets = np.zeros(market_count)
        time_stack_check = 0.0

        #가격 변동파악-1
        if market_count>=100:
            prices = np.asarray(list(pu.get_current_price(markets[:100]).values()))
            prices = np.hstack((prices,list(pu.get_current_price(markets[100:]).values())))
        else:
            prices = np.asarray(list(pu.get_current_price(markets[:]).values()))

        time_first = time.time()
        
        while True:
                #마켓 변동 사항 파악
                buy_markets,ordered_markets = get_buy_markets()
                time.sleep(SLEEP_TIME)

                #판매
                delete_market_list = []
                total_balance = get_balances()
                time.sleep(SLEEP_TIME)

                for index,b_m in enumerate(buy_markets):
                    for bal_info in total_balance:
                        if 'KRW-'+bal_info['currency'] == b_m:
                            time_info = pu.get_ohlcv(b_m,interval='minute1',count=10)['close']
                            time.sleep(SLEEP_TIME)

                            four_time_line =  time_info.rolling(4).mean()[-1]
                            two_time_line = time_info.rolling(2).mean()[-1]
                            
                            if (two_time_line <= four_time_line) or (stack_markets[markets.index(b_m)]<=SELL_STACK):
                                avg_buy_price = float(bal_info['avg_buy_price'])

                                balance = bal_info['balance']
                            
                                current_price = pu.get_current_price(b_m)
                                time.sleep(SLEEP_TIME)
                                change_val_avg =((current_price - avg_buy_price)/ avg_buy_price)* 100
                                
                                if change_val_avg>= SELL_MIN_VAL:
                                    sell_market_order(b_m,balance)
                                    time.sleep(SLEEP_TIME)
                                    delete_market_list.append(b_m)
                            
                            break

                for _ in delete_market_list:
                    buy_markets.remove(_)
                    print('sell : {}, markets : {}'.format(_,buy_markets))
                
                #가격 변동 파라미터 초기화
                if time_stack_check >= CHECK_TIME_SELL:
                    time_stack_check = 0.0
                    stack_markets = np.zeros(market_count)

                #가격 변동 파악-2
                if market_count>=100:
                    prices_now = np.asarray(list(pu.get_current_price(markets[:100]).values()))
                    prices_now = np.hstack((prices_now,list(pu.get_current_price(markets[100:]).values())))
                else:
                    prices_now = np.asarray(list(pu.get_current_price(markets[:]).values()))           

                time_last = time.time()
                time_stack_check += (time_last - time_first)
                time_first = time_last     
                
                change_val = ((prices_now-prices)/prices)*100
                prices = prices_now
                stack_markets += change_val
                
    except KeyboardInterrupt:
        pass
        
if __name__ == "__main__":
    SLEEP_TIME = float(sys.argv[1])
    CHECK_TIME_SELL = int(sys.argv[2])
    markets = ast.literal_eval(sys.argv[3])
    market_count = int(sys.argv[4])
    SELL_MIN_VAL = float(sys.argv[5])
    SELL_STACK = float(sys.argv[6])
    
    main(SLEEP_TIME,CHECK_TIME_SELL,markets,market_count,SELL_MIN_VAL,SELL_STACK)