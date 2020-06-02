# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 15:44:00 2020

@author: Nag
"""

# -*- coding: utf-8 -*-
"""
Created on Wed May 27 19:57:09 2020

@author: Nag
"""




import hmac
import hashlib
import base64
import json
import time
import requests
from decimal import Decimal

coin_api="paste key here"
coin_secret="paste secret here"


ticker_url = "https://api.coindcx.com/exchange/"
exit_url = "https://api.coindcx.com/exchange/v1/margin/exit"
cancel_url = "https://api.coindcx.com/exchange/v1/margin/cancel"
fetch_url = "https://api.coindcx.com/exchange/v1/margin/fetch_orders"
place_url="https://api.coindcx.com/exchange/v1/margin/create"
cancel_by_ids_url = "https://api.coindcx.com/exchange/v1/orders/cancel_by_ids"
SL_url = "https://api.coindcx.com/exchange/v1/margin/edit_sl"
target_url = "https://api.coindcx.com/exchange/v1/margin/edit_target"
unit=0.0001
usdt=10000



open_orders=[]
specs_orders=[]

# Enter your API Key and Secret here. If you don't have one, you can generate it from the website.
key = coin_api
secret = coin_secret

# python3
secret_bytes = bytes(secret, encoding='utf-8')

def timeStamp():
    return int(round(time.time() * 1000))

fetch_open_orders_body = {
  "details": True,
  "timestamp": timeStamp(),
  #"status": "close",
  "page":1,
  "size":500
}

def jsonify(body) :
	 return json.dumps(body, separators = (',', ':'))

def headersf(body):
    json_body = jsonify(body)
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    return {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': key,
        'X-AUTH-SIGNATURE': signature
    }


'''  Base function to execute a query takes the url and parameters as json ody '''
def transact(url,body):
	try:
		response = requests.post(url, data = jsonify(body), headers = headersf(body))
		return response.json()
	except:print(response)

'''  creates order body along with stop loss and target '''

def create_order_body_ST(orders):
	_orders=[]
	_ls=None
	for order in orders:
	  
	  _ls=[]
	  _ls.append({
	  "side": order['side'],
	  "order_type": order["order_type"],
	  "market": order["market"],
	  "price": order["price"],
	  "quantity": order["quantity"],
	  "ecode": 'B',
	  "leverage": order["leverage"],
	  "timestamp": timeStamp()
	  })
	  _ls.append(order['sl_price'])
	  _ls.append(order['target_price'])
	  #print(_orders)
	  _orders.append(_ls)
	return _orders

'''  creates order body  '''


def create_order_body(orders):
	_orders=[]
	for order in orders:
	  _orders.append({
	  "side": order['side'],
	  "order_type": order["order_type"],
	  "market": order["market"],
	  "price": order["price"],
	  "quantity": order["quantity"],
	  "ecode": 'B',
	  "leverage": order["leverage"],
	  "timestamp": timeStamp()
	  })
	return _orders


''' fegch all the orders by pair '''
def fetch_by_pair(pair):
	open_orders=[]
	body = {
	"side": "buy", # Toggle between a 'buy' or 'sell' order.
	"market": pair.upper(), # Replace 'SNTBTC' with your desired market pair.
	"timestamp": timeStamp(),
	"page":1,
	"size":500
	}

	response = requests.post(fetch_url, data = jsonify(body), headers = headersf(body))
	
	data = response.json()
	#print(data)
	for x in data:
		if x["status"] != "cancelled":
			open_orders.append(x)
			price = str(round( Decimal( x["price"] ) ,8) )
			print(x["market"],x["status"],price,round(x['price']*x['quantity']*1000,2))
	return open_orders

''' fetch orders by specifications like status , market ,order type  '''

def fetch(specification,condition):
    open_orders=[]
    response = requests.post(fetch_url, data = jsonify(fetch_open_orders_body), headers = headersf(fetch_open_orders_body))
    data = response.json()
    #print(data,123,)
    for x in data:
        #print(x['market'],end="\n") 
        #print(x,123)
        if x[specification]==condition and x['price'] >0.0000002  and x["status"] != "cancelled":
            price = str(round( Decimal( x["price"] ) ,8) )
            print(x['market'],price,round(x['price']*x['quantity']*1000,2),x['status'],end="") 
            print("----- fetch----")
            open_orders.append(x)
    return open_orders


''' updates the stop loss of an order given its id and price  '''
def update_SL(id,price):
	_res = transact(SL_url,{'id':id , 'sl_price':price,'timeStamp':timeStamp() })
	return _res
	

''' updates the target of an order given its id and targetprice  '''

def update_target(id,price):
	_res = transact(target_url,{'id':id , 'target_price':price,'timeStamp':timeStamp() })
	return _res

''' get ids given a list of orders in json format  '''

def get_ids(orders):
	_ids=[]
	for x in orders:
		_ids.append(x['id'])
	return _ids
#order_body=create_order_body(open_orders)

'''  place an order given parameters in json '''
def place_order(body):
	return transact(place_url,body)
	
'''  place  orders and also updates stop loss and target price  given parameters in list of orders in json format '''
#the input will be the return value of create_order_body_ST function

def place_multiple_orders2(orders):
	_body=create_order_body(orders)
	_st=create_order_body_ST(orders)
	print(_st)
	for x in _st:
		try:
			print(x[0]["market"],x[0]["price"],"-----multiple orders ----\n")
			_res=transact(place_url,x[0])
			print("ress----",_res)
			print(update_SL(_res[0]['id'],x[1]))
			print(update_target(_res[0]['id'],x[2]))
		except:
			print(x[0]["market"])


'''  place  orders given parameters in list of orders in json format '''
#input will be the return value of create_orders function

def place_multiple_orders(orders):
	_body=create_order_body(orders)
	#_st=create_order_body_ST(orders)
	for x in _body:
		print(x,"-----multiple orders ----\n")
		_res=transact(place_url,x)
		print(_res)


def cancel_by_pair(pair):
	my_orders=fetch("market",pair.upper())
	cancel_multiple_orders(my_orders)


def cancel_multiple_orders(orders):
	#open_orders=fetch("status","init")
	_ids=get_ids(orders)
	print(_ids,"-----camcel--------")
	for x in _ids:
		print("cancel response ",transact(cancel_url,{
				"id":x,"timestamp":timeStamp() 
				}))

def make_order(side,otype,pair,price,size):
	print((size*unit)/price,float(size*unit))
	return {'side': side.lower(), 'order_type': otype, 'market': pair.upper(),
	  'price': price, 'quantity':int(size*unit/price) , 'ecode': 'B', 'leverage': 3.0, 'timestamp': timeStamp()}


def make_order_usd_pair(side,otype,pair,price,size,precision):
	print(size/price,round(size/price,precision))
	return {'side': side.lower(), 'order_type': otype, 'market': pair.upper(),
	  'price': price, 'quantity':round(size/price,precision) , 'ecode': 'B', 'leverage': 3.0, 'timestamp': timeStamp()}


'''exit an existing position '''
def exit_position_by_pair(pair):
	orders=fetch_by_pair(pair)
	for x in orders:
		transact( exit_url , { "id":x["id"] , "timeStamp":timeStamp() })


''' works for shitcoins only 
1 unit size is 1/10000 btc. eg size = 2 means 0.0002 btc
use this for btc pair only
'''

def set_limit_order(pair,price,size):
	 precision=2
	 if price < 0.0002:precision=0
	 elif price > 0.01:precision=3
	 body = {'side': "buy", 'order_type': "limit_order", 'market': pair.upper(),
		  'price': price, 'quantity':round((size*unit)/price,precision) , 'ecode': 'B', 'leverage': 3.0, 'timestamp': timeStamp()}
	 print(body)
	 return transact(place_url,body)


'''cancel and open prders'''

def run():
	open_orders=fetch("status","init")
	cancel_multiple_orders(open_orders)
	place_multiple_orders2(open_orders)


#examples of useful functions

# 1.set_limit_order(pair,price,size)
#1 unit size is 0.0001 btc. eg size = 15 means 0.0015 btc


print(set_limit_order("ltcbtc",0.0042,8)) # size 0.0008 
print(set_limit_order("ltcbtc",0.0045,7)) # size 0.0007
print(set_limit_order("ltcbtc",0.006,2)) # size 0.0006


#--exitss all eth btc orders
print(exit_position_by_pair("ltcbtc"))

#--cancels all ltc btc orders
print(cancel_by_pair("ltcbtc"))

#fetch all the orders by ltcbtc
print(fetch_by_pair("ltcbtc"))


#run()


