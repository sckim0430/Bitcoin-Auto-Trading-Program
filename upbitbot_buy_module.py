import sys
import pyupbit as pu
import time
import numpy as np
from auto_trading import get_buy_markets, get_total_balance, get_balance, buy_market_order
import ast


def main(FEE, MIN_ORDER_PRICE, BUY_STACK, SLEEP_TIME, CHECK_TIME, DAY_CHECK_TIME,
         MAX_COIN_COUNT, markets, market_count, day_markets):
    try:
        stack_markets = np.zeros(market_count)
        stack_markets_order = np.zeros(market_count)
        stack_markets_order_index = np.zeros(market_count)

        time_stack_check = 0.0
        time_day_check = 0.0

        #가격 변동파악-1
        if market_count >= 100:
            prices = np.asarray(
                list(pu.get_current_price(markets[:100]).values()))
            prices = np.hstack(
                (prices, list(pu.get_current_price(markets[100:]).values())))
        else:
            prices = np.asarray(
                list(pu.get_current_price(markets[:]).values()))

        time_first = time.time()

        while True:
            #마켓 변동 사항 파악
            buy_markets, ordered_markets = get_buy_markets()

            #구매
            positive_price = get_balance("KRW")
            time.sleep(SLEEP_TIME)

            if positive_price >= MIN_ORDER_PRICE * (1/FEE) and not (stack_markets_order == np.zeros(market_count)).min():
                for index, s in enumerate(stack_markets_order):
                    if len(buy_markets) >= MAX_COIN_COUNT:
                        break

                    if day_markets[stack_markets_order_index[index]] and (s >= BUY_STACK) and (markets[stack_markets_order_index[index]] not in buy_markets) and (markets[stack_markets_order_index[index]] not in ordered_markets):
                        positive_price = get_balance("KRW")
                        time.sleep(SLEEP_TIME)

                        if positive_price >= MIN_ORDER_PRICE * (1/FEE):
                            vol_check = pu.get_ohlcv(
                                markets[stack_markets_order_index[index]], interval='minute1', count=200)
                            time.sleep(SLEEP_TIME)

                            vol_now = vol_check['volume'][-1]
                            vol_avg = vol_check['volume'].mean()
                            time_info = vol_check['close'][-30:]

                            current_price = time_info[-1]
                            twenty_time_line = np.asarray(
                                list(time_info.rolling(20).mean()[-6:]))
                            ten_time_line = np.asarray(
                                list(time_info.rolling(10).mean()[-6:]))
                            five_time_line = np.asarray(
                                list(time_info.rolling(5).mean()[-6:]))

                            is_accend = (five_time_line[-1] >= ten_time_line[-1]) and (
                                ten_time_line[-1] >= twenty_time_line[-1])
                            is_near_point = (len(set(five_time_line >= ten_time_line)) == 2) and (
                                len(set(ten_time_line >= twenty_time_line)) == 2)

                            if is_accend and is_near_point and (vol_now >= vol_avg*BUY_STACK):
                                BUY_BALANCE = positive_price / \
                                    (MAX_COIN_COUNT-len(buy_markets))
                                order_price = BUY_BALANCE*FEE

                                buy_market_order(
                                    markets[stack_markets_order_index[index]], order_price)
                                time.sleep(SLEEP_TIME)
                                buy_markets.append(
                                    markets[stack_markets_order_index[index]])
                                print('buy : {}, markets : {}, order_price : {}'.format(
                                    markets[stack_markets_order_index[index]], buy_markets, order_price))
                        else:
                            break

            #가격 변동 파라미터 초기화
            if time_stack_check >= CHECK_TIME:
                time_stack_check = 0.0
                stack_markets = np.zeros(market_count)
                stack_markets_order = np.zeros(market_count)
                stack_markets_order_index = np.zeros(market_count)

            #최고가 및 마켓 각 코인의 상승장 여부 파악
            if time_day_check >= DAY_CHECK_TIME:
                time_day_check = 0.0

                day_markets.clear()

                for market in markets:
                    day_info = pu.get_ohlcv(
                        market, interval='day', count=13)['close']
                    time.sleep(SLEEP_TIME)
                    ten_day_line = np.asarray(
                        list(day_info.rolling(10).mean()[-3:]))
                    five_day_line = np.asarray(
                        list(day_info.rolling(5).mean()[-3:]))

                    day_markets.append((five_day_line > ten_day_line).min())

            #가격 변동 파악-2
            if market_count >= 100:
                prices_now = np.asarray(
                    list(pu.get_current_price(markets[:100]).values()))
                prices_now = np.hstack(
                    (prices_now, list(pu.get_current_price(markets[100:]).values())))
            else:
                prices_now = np.asarray(
                    list(pu.get_current_price(markets[:]).values()))

            time_last = time.time()
            time_stack_check += (time_last - time_first)
            time_day_check += (time_last - time_first)

            time_first = time_last

            change_val = ((prices_now-prices)/prices)*100
            prices = prices_now

            stack_markets += change_val
            stack_markets_order = np.sort(stack_markets)[::-1]
            stack_markets_order_index = (-stack_markets).argsort()

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    FEE = float(sys.argv[1])
    MIN_ORDER_PRICE = int(sys.argv[2])
    BUY_STACK = float(sys.argv[3])
    SLEEP_TIME = float(sys.argv[4])
    CHECK_TIME = int(sys.argv[5])
    DAY_CHECK_TIME = int(sys.argv[6])
    MAX_COIN_COUNT = int(sys.argv[7])
    markets = ast.literal_eval(sys.argv[8])
    market_count = int(sys.argv[9])
    day_markets = ast.literal_eval(sys.argv[10])

    main(FEE, MIN_ORDER_PRICE, BUY_STACK, SLEEP_TIME, CHECK_TIME,
         DAY_CHECK_TIME, MAX_COIN_COUNT, markets, market_count, day_markets)
