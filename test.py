import requests
import bcrypt
import pybase64
import time
import urllib.request
import urllib.parse

class Authentification:
    def __init__(self):
        self.base_url='https://api.commerce.naver.com/external/v1'
        self.client_id='2sNZ6cclKObW9q5RAiiPBd'
        self.client_secret='$2a$04$NP.zZOrB3DHygKqOZ9TsBu'

    def get_token(self, type_="SELF") -> str:
        timestamp = str(int((time.time()-3) * 1000))

        # Make a password by connecting client id and timestamp with '_'
        pwd = f'{self.client_id}_{timestamp}'
        # bcrypt hashing
        hashed = bcrypt.hashpw(pwd.encode('utf-8'), self.client_secret.encode('utf-8'))
        # base64 encoding
        client_secret_sign = pybase64.standard_b64encode(hashed).decode('utf-8')

        headers = {"content-type": "application/x-www-form-urlencoded"}
        data_ = {
            "client_id": self.client_id,
            "timestamp": timestamp,
            "client_secret_sign": client_secret_sign,
            "grant_type": "client_credentials",
            "type": type_
        }

        query = urllib.parse.urlencode(data_)
        url = self.base_url + '/oauth2/token?' + query
        res = requests.post(url=url, headers=headers)
        res_data = res.json()

        while True:
            if 'access_token' in res_data:
                token = res_data['access_token']
                return token
            else:
                print(f'[{res_data}] 토큰 요청 실패')
                time.sleep(1)

def get_new_order_list(token_):
    from datetime import datetime, timedelta

    headers = {'Authorization': token_}
    url = 'https://api.commerce.naver.com/external/v1/pay-order/seller/product-orders/last-changed-statuses'
    
    now = datetime.now()
    # before_date = now - timedelta(hours=3) #3시간전
    # before_date = now - timedelta(seconds=10) #10초전
    # before_date = now - timedelta(minutes=10) #10분전
    before_date = now - timedelta(days=2) #이틀전
    iosFormat = before_date.astimezone().isoformat()

    params = {
            'lastChangedFrom' : iosFormat, #조회시작일시
            'lastChangedType' : 'DISPATCHED', #최종변경구분(PAYED : 결제완료, DISPATCHED : 발송처리)
        }

    res = requests.get(url=url, headers=headers, params=params)
    res_data = res.json()

    if 'data' not in res_data: #조회된 정보가 없을 경우 data키 없음
        print('주문 내역 없음')
        return False

    data_list = res_data['data']['lastChangeStatuses']

    for data in data_list:
        print(data) #주문 정보

def get_order_detail(token_):
    import datetime

    headers = {'Authorization': token_}
    url = 'https://api.commerce.naver.com/external/v1/pay-order/seller/product-orders/query'
    
    params = {
        'productOrderIds' : ['']
    }

    res = requests.post(url=url, headers=headers, json=params)
    res_data = res.json()
    
    # print(res_data)
    if 'data' not in res_data:
        return False
    
    for data in res_data['data']:
        for d in data.keys():
            for d2 in data[d].keys():
                print(f'{d2} : {data[d][d2]}')

def item_sending(token_, productOrderIds, dispatchDate):
    headers = {
        'Authorization': token_,
        'content-type': "application/json"
        }
    url = 'https://api.commerce.naver.com/external/v1/pay-order/seller/product-orders/dispatch'
    
    params = {
        'dispatchProductOrders' : [{
            'productOrderId' : str(productOrderIds[0]),
            'deliveryMethod' : 'NOTHING',
            'dispatchDate' : dispatchDate, #배송일
    }]}

    res = requests.post(url=url, headers=headers, json=params)
    res_data = res.json()
    
    print(res_data)
    if 'data' not in res_data:
        return False

auth = Authentification()
token = auth.get_token()
print(f'발급된 토큰 : ', token)
get_new_order_list(token)
get_order_detail(token)