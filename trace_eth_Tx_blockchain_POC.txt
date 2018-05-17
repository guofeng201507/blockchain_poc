# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 21:25:59 2018

@author: guof

https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API#get-address-info

0xc5d431ee2470484b94ce5660aa6ae835346abb19

0x10abb5efecdc09581f8b7cb95791fe2936790b4e
0xb3764761e297d6f121e79c32a65829cd1ddb4d32

"""

import json
import urllib.request
import time

monitor_addr = set()

address_1 = '0xb297cacf0f91c86dd9d2fb47c6d12783121ab780'
addr_empty = '0xc5d431ee2470484b94ce5660aa6ae835346abb19'

def getAddrBal(address):
    #website = 'https://api.ethplorer.io/'
    api = 'getAddressInfo/'
    the_url = 'https://api.ethplorer.io/' + api + address + '?apiKey=freekey'
    
    print(the_url)
    #address_bal_request = urllib.request.Request(url='https://api.ethplorer.io/getAddressInfo/0xff71cb760666ab06aa73f34995b42dd4b85ea07b?apiKey=freekey' ,
    address_bal_request = urllib.request.Request(url=the_url, 
                                                 data=None,
                                 headers={
                                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4'
                                })
    
    address_bal_eth = urllib.request.urlopen(address_bal_request).read().decode('UTF-8')
    address_bal_eth_data = json.loads(address_bal_eth)
    
    #print(address_bal_eth_data['ETH'])
    return address_bal_eth_data['ETH']['balance']

def getTargetAddr(address):
    
    temp_addr_set = set()
    the_url2 = 'https://api.ethplorer.io/getAddressTransactions/' + address + '?apiKey=freekey'
    print(the_url2)
#address_request = urllib.request.Request(url='https://api.ethplorer.io/getAddressTransactions/0xb297cacf0f91c86dd9d2fb47c6d12783121ab780?apiKey=freekey', 
    address_request = urllib.request.Request(url=the_url2, 
                                         data=None,
                             headers={
                                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4'
                            })

    address_eth = urllib.request.urlopen(address_request).read().decode('UTF-8')
    address_eth_data = json.loads(address_eth)
    
    for x in address_eth_data:
        #print(x)
        if x['from'] == address:
            temp_addr_set.add(x['to'])
    
    print(temp_addr_set)
    return list(temp_addr_set)

#print(getTargetAddr(address))
def process(address, monitor_addr):

        if getAddrBal(address) < 0.00063:
            print('balance is zero, check further')
            for _addr in getTargetAddr(address):
                #print('Recurssive call starts')
                #time.sleep(5)
                process(_addr, monitor_addr)
        else:
            print('balance is not zero, stop check ')
            if not address in monitor_addr:
                print('New wallet found ')
                monitor_addr.add(address)     
                f= open("guru99.txt","a+")
                f.write('\n' + address)
                f.close()            
            return monitor_addr                    


print(process(addr_empty, monitor_addr))

def monitor(address, monitor_addr):
    time.sleep(10)
    process(address, monitor_addr)          

    return monitor_addr

"""
if getAddrBal(x['to']) > 0:
   print('Found the wallet address which has balance, add to monitor list')
else:
   susp_addr.add(x['to'])

"""