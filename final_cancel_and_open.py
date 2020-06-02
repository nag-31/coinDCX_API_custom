# -*- coding: utf-8 -*-
"""
Created on Wed May 13 20:26:43 2020

@author: Nag
"""

import hmac
import hashlib
import base64
import json
import time
import requests

coin_api="paste ur api here"
coin_secret="paste your secret here"

cancel_url = "https://api.coindcx.com/exchange/v1/margin/cancel"
fetch_url = "https://api.coindcx.com/exchange/v1/margin/fetch_orders"
place_url="https://api.coindcx.com/exchange/v1/margin/create"
cancel_by_ids_url = "https://api.coindcx.com/exchange/v1/orders/cancel_by_ids"
SL_url = "https://api.coindcx.com/exchange/v1/margin/edit_sl"
target_url = "https://api.coindcx.com/exchange/v1/margin/edit_target"
unit=0.0001
usdt=10000

# Enter your API Key and Secret here. If you don't have one, you can generate it from the website.
key = coin_api
secret = coin_secret

# python3
secret_bytes = bytes(secret, encoding='utf-8')
# python2
#secret_bytes = bytes(secret)

# Generating a timestamp.
def timeStamp():
    return int(round(time.time() * 1000))

fetch_open_orders_body = {
  "details": True,
  "timestamp": timeStamp(),
  #"status": "close",
  "page":1,
  "size":100
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


def transact(url,body):
	try:
		response = requests.post(url, data = jsonify(body), headers = headersf(body))
		return response.json()
	except:print(response)


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


open_orders=[]
specs_orders=[]
def fetch_by_specs(specs,conditions):
	specs_orders=[]
	try:
		response = requests.post(fetch_url, data = jsonify(fetch_open_orders_body), headers = headersf(fetch_open_orders_body))
		data = response.json()
		for x in range(len(specs)):
			pass
	except Exception as e:print(e)


def fetch(specification,condition):
    open_orders=[]
    response = requests.post(fetch_url, data = jsonify(fetch_open_orders_body), headers = headersf(fetch_open_orders_body))
    data = response.json()
    #print(data,123,)
    for x in data:
        #print(x['market'],end="\n") 
        #print(x,123)
        if x[specification]==condition and x['price'] >0.0000002 :
            print(x['market'],x['id'],end="") 
            print("----- fetch----")
            open_orders.append(x)
    return open_orders
def update_SL(id,price):
	_res = transact(SL_url,{'id':id , 'sl_price':price,'timeStamp':timeStamp() })
	return _res
	


def update_target(id,price):
	_res = transact(target_url,{'id':id , 'target_price':price,'timeStamp':timeStamp() })
	return _res


def get_ids(orders):
	_ids=[]
	for x in orders:
		_ids.append(x['id'])
	return _ids
#order_body=create_order_body(open_orders)

def place_order(body):
	return transact(place_url,body)
	

def place_multiple_orders2(orders):
	_body=create_order_body(orders)
	_st=create_order_body_ST(orders)
	for x in _st:
		print(x,"-----multiple orders ----\n")
		_res=transact(place_url,x[0])
		print("ress----",_res)
		print(update_SL(_res[0]['id'],x[1]))
		print(update_target(_res[0]['id'],x[2]))


def place_multiple_orders(orders):
	_body=create_order_body(orders)
	#_st=create_order_body_ST(orders)
	for x in _body:
		print(x,"-----multiple orders ----\n")
		_res=transact(place_url,x)
		print(_res)
#		print(update_SL(_res['id'],x[1]))
#		print(update_target(_res['id'],x[2]))

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


def make_order_usd_pair(side,otype,pair,price,size):
	print(size/price,round(size/price,5))
	return {'side': side.lower(), 'order_type': otype, 'market': pair.upper(),
	  'price': price, 'quantity':round(size/price,5) , 'ecode': 'B', 'leverage': 4.0, 'timestamp': timeStamp()}


#transact(cancel_by_ids_url,{"ids":['14cc935f-3f35-47fb-b9a9-5bcc4229271f', 'd13a36e9-38af-4975-9a9e-3cdc065ebb48', 'f3e18dbf-4579-45ae-b5af-6c346768707a']})
def cancel_last_n_init_orders(n):
	fetch("status","init")
	try:
		print(open_orders[n],"to cancel order")
	except:print("error")	
	cancel_multiple_orders(open_orders[:n])

def place_trail_orders_by_diff(side,order_type,pair,price,size,diff,n):
	decimals=len(str(price))-len(str(int(price)))-1
	print(decimals,str(price),str(int(price)))
	for x in range(n):
		price=price-(price*diff*.01)
		
		

#open_orders=fetch("status","init")

#cancel_last_n_init_orders(3)
'''cancel and open prders'''
def run():
	open_orders=fetch("status","init")
	cancel_multiple_orders(open_orders)
	place_multiple_orders2(open_orders)

#place_trail_orders_by_diff('buy','limit_order','ethusdt',0.00000021,11*usdt,1,5)







#print(create_order_body_ST(open_orders))
#print(update_SL('2d8bef90-f655-4b67-bc1a-c3120d605924',7000))
#print(update_target('2d8bef90-f655-4b67-bc1a-c3120d605924',11000))
#ordd= {'side': 'buy', 'order_type': 'limit_order', 'market': 'CELRBTC',
#	  'price': 0.00000026, 'quantity': 3000, 'ecode': 'B', 'leverage': 4.0, 'timestamp': timeStamp()}
#
'''create orders'''
#print(place_order(ordd))print(place_order(make_order('buy','limit_order','onebtc',0.00000031,6)))

#print(place_order(make_order('buy','limit_order','onebtc',0.00000035,3)))
#print(place_order(make_order('buy','limit_order','celrbtc',0.00000025,6)))
#print(place_order(make_order('buy','limit_order','fetbtc',0.00000208,8)))
#print(place_order(make_order('buy','limit_order','maticbtc',0.00000197,4)))
#print(place_order(make_order('buy','limit_order','xembtc',0.00000411,3)))
#print(place_order(make_order('buy','limit_order','nasbtc',0.0000285,6)))
#print(place_order(make_order('buy','limit_order','stxusdt',0.113,11*usdt)))
#print(place_order(make_order('buy','limit_order','nanobtc',0.0000774,3)))
#print(place_order(make_order('buy','limit_order','ostbtc',0.00000068,3)))
#print(place_order(make_order('buy','limit_order','hbarbtc',0.00000365,7)))
print(place_order(make_order('buy','limit_order','solbtc',0.000064,2)))
print(place_order(make_order('buy','limit_order','solbtc',0.0000625,2)))
print(place_order(make_order('buy','limit_order','solbtc',0.000062,2)))
print(place_order(make_order('buy','limit_order','solbtc',0.0000615,2)))
print(place_order(make_order('buy','limit_order','solbtc',0.000063,2)))

#print(place_order(make_order('buy','limit_order','hbarbtc',0.00000365,3)))
#print(place_order(make_order('buy','limit_order','beambtc',0.000035,3)))
#print(place_order(make_order('buy','limit_order','thetabtc',0.0000190,3)))

#print(place_order(make_order('buy','limit_order','zrxbtc',0.000037,2)))


'''btc orders'''
#price=8930
#
#for x in range(6):
#	print(place_order(make_order_usd_pair('buy','limit_order','btcusdt',price,11)))
#	price=price-20

#print(place_order(make_order('buy','limit_order','btcusdt',8960,11*usdt)))

'''eth orders'''
#eth_price=173
##
#for x in range(5):
#	print(place_order(make_order_usd_pair('buy','limit_order','ethusdt',eth_price,11)))
#	eth_price=round(eth_price-0.8,2)
#	print(eth_price)

#print(place_order(make_order('buy','limit_order','btcusdt',8960,11*usdt)))


run()
