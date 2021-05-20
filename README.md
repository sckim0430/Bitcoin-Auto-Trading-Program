# Upbit Auto Trading Program
   
<p align="left"><img src="https://user-images.githubusercontent.com/63839581/118985117-24a7d800-b9b9-11eb-9e72-64f148bc72d0.jpg" width="600"></p>   
   
## Description
   
이 저장소는 가상화폐 거래소인 **업비트 원화 마켓 자동 매매 프로그램**을 주제로 구현되었습니다.   
   
## Installation
   
Python 3.6 이상의 버전이 필요합니다. [Anaconda](https://www.anaconda.com/)설치를 추천합니다.   
이 저장소는 [PyUpbit](https://github.com/sharebook-kr/pyupbit)에서 제공되는 API를 기반으로 작성되었습니다. 기본 API는 숙지는 해당 저장소에서 숙지해주시길 바랍니다.
   
pyupbit와 pyjwt를 설치합니다.   

```bash
$ pip install pyupbit
```   
   
```bash
$ pip install pyjwt
```   
   
## Start
   
시작하기에 앞서, 업비트의 API 지원 항목에서 access key와 secret key를 할당받고, [auto_trading.py](https://github.com/sckim0430/Upbit-Auto-Trading-Program/blob/master/auto_trading.py)에서 다음 부분을 작성합니다.   
   
```bash
access = ''
secret = ''
```   
   
[auto_trading.py](https://github.com/sckim0430/Upbit-Auto-Trading-Program/blob/master/auto_trading.py)에서 파라미터들을 수정한 뒤, 프로그램을 실행합니다.   
   
```bash
python auto_trading.py
```   
   
매수와 관련된 코드는 [upbitbot_buy_module.py](https://github.com/sckim0430/Upbit-Auto-Trading-Program/blob/master/upbitbot_buy_module.py), 매도와 관련된 코드는 [upbitbot_sell_module.py ](https://github.com/sckim0430/Upbit-Auto-Trading-Program/blob/master/upbitbot_sell_module.py)에서 살펴볼 수 있습니다.   
**멀티 프로세싱**으로 구현하여 매수와 매도 기능을 선택적으로 사용할 수 있습니다. [auto_trading.py](https://github.com/sckim0430/Upbit-Auto-Trading-Program/blob/master/auto_trading.py)에서 다음 부분을 수정해주시면 됩니다.   
   
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
   
다음 주의 사항들을 숙지해주시길 바랍니다.   
   
1. 해당 코드는 원화 마켓(KRW)을 전용으로 구현하였습니다.   
   
2. 마켓의 정보가 바뀐 경우(상장 폐지, 신규 상장 등)나 업비트 점검 시 프로그램을 사용을 지양해주시길 바랍니다.   
   
3. 시장 상황에 따라 수익률이 달라질 수 있으므로, 충분히 테스트를 해보고 사용해주시길 바랍니다.   
   
4. 프로그램 시작 시, 이미 구매된 코인중에서 지정가 주문을 하지 않은 경우 매도 프로그램에 의해 바로 매도 될 수 있으니 유의하시길 바랍니다.   
   
## Contact
   
another0430@naver.com
