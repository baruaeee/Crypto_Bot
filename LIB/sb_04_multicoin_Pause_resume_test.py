from binance.client import Client
from pynput import keyboard
from datetime import datetime
from decimal import Decimal
import pandas as pd
import time
import os
import traceback
import sys

import getpass

# ----Get the input securely----
api_key = getpass.getpass("Enter your API key: ")
api_secret = getpass.getpass("Enter your secret: ")

# ----initialize the Binanace client (testnet argument is not necessary in actual binance)----
client = Client(api_key, api_secret)

# ----Read crypto prices----
def read_price(crypto):
    return client.get_ticker(symbol=crypto)['lastPrice']

def read_param(coin_pair, x):
    df = pd.read_csv('conf.csv', sep=', ', engine='python')
    row = df.index[df['pair'] == coin_pair].tolist()[0]
    data = df.at[row, x]
    return data

def reb(coin_pair):
    count = 0
    qty_min = Decimal(str(client.get_symbol_info(coin_pair)['filters'][1]['minQty'])).normalize()
    buy_frac = read_param(coin_pair, 'buy_frac')
    sell_frac = read_param(coin_pair, 'sell_frac')
    coin_dist = read_param(coin_pair, 'coin_dist')
    pair_min = read_param(coin_pair, 'pair_min')
    pair_max = read_param(coin_pair, 'pair_max')
    div = read_param(coin_pair, 'div')

    if str(qty_min).isdigit():
        qty_rnd = 0
    else:
        qty_rnd = len(str(qty_min).split('.')[1])

    if coin_pair[-4:] == 'USDT':
        base_coin = 'USDT'
        coin = coin_pair[:(len(coin_pair)-4)]
    else:
        base_coin = coin_pair[-3:]
        coin = coin_pair[:(len(coin_pair)-3)]

    base = float(client.get_asset_balance(asset=base_coin)['free'])
    if base_coin != 'USDT':
        base_USDT = float(read_price(base_coin+'USDT'))
        base_USD_Balance = base_USDT*base
    else:
        base_USD_Balance = base

    crypto = float(client.get_asset_balance(asset=coin)['free'])
    crypto_USDT = float(read_price(coin+'USDT'))
    crypto_USD_Balance = crypto_USDT*crypto

    if coin_dist != 0:
        crypto_frac_calc = coin_dist
    elif coin_dist == 0 and pair_min == 0 and pair_max == 0:
        crypto_frac_calc = coin_dist
    else:
        crypto_pair = float(read_price(coin_pair))
        crypto_frac_calc = (0.1 - (0.8*(crypto_pair - pair_max)/(pair_max - pair_min)))/div

    base_frac_calc = 1 - crypto_frac_calc

    crypto_adj = ((crypto_frac_calc*(crypto_USD_Balance+base_USD_Balance))-crypto_USD_Balance)/crypto_USDT
    crypto_trade = round(abs(crypto_adj), qty_rnd)

    if crypto == 0:
        trade_percent = 100
    else:
        trade_percent = crypto_trade*100/crypto

    try:
        if crypto_adj < 0 and trade_percent >= sell_frac:
            client.create_order(symbol=coin_pair, side='SELL', type='MARKET', quantity=crypto_trade)
            print(str(crypto_trade) + ' ' + coin + '-' + coin_pair + ' sold')
            count = count+1
        elif crypto_adj > 0 and trade_percent >= buy_frac:
            client.create_order(symbol=coin_pair, side='BUY', type='MARKET', quantity=crypto_trade)
            print(str(crypto_trade) + ' ' + coin + '-' + coin_pair + ' bought')
            count = count+1
    except Exception as e:
        print(coin_pair + " Execution Error!", e)
        traceback.print_exc()

    return count

def rebalance():
    df = pd.read_csv('conf.csv', sep=', ', engine='python')
    trade_count = 0
    for index, row in df.iterrows():
        if trade_count == 0:
            trade_count = trade_count + reb(row['pair'])
    return trade_count

def print_status():
    df = pd.read_csv('conf.csv', sep=', ', engine='python')
    lst = []
    for index, row in df.iterrows():
        if row['pair'][-4:] == 'USDT':
            base_coin = 'USDT'
            coin = row['pair'][:(len(row['pair'])-4)]
        else:
            base_coin = row['pair'][-3:]
            coin = row['pair'][:(len(row['pair'])-3)]
        lst.extend([coin, base_coin])
    lst = list(set(lst))
    data = []
    total = 0
    for i in lst:
        crypto = float(client.get_asset_balance(asset=i)['free'])
        if i != 'USDT':
            crypto_USDT = float(read_price(i+'USDT'))
            crypto_USD_Balance = crypto*crypto_USDT
        else:
            crypto_USD_Balance = crypto
        data.append({'Coin': i, 'Blnc': crypto, '$Blnc': crypto_USD_Balance})
        total = total + crypto_USD_Balance
    for i in data:
        i['Dist'] = str(round(i['$Blnc']*100/total, 2))+'%'
    dfn = pd.DataFrame(data)
    now = datetime.now()
    print(now.strftime('%d/%m/%Y %H:%M:%S'))
    print(dfn)
    print('Total USD:'+str(total))

paused = False
pause_message_printed = False

def on_press(key):
    global paused, pause_message_printed
    if key == keyboard.Key.f1:
        paused = not paused
        pause_message_printed = False  # Reset the message printed flag
        print("Script paused" if paused else "Script resumed")

listener = keyboard.Listener(on_press=on_press)
listener.start()

while True:
    try:
        if not paused:
            os.system('clear')
            print('BOT is running ...')
            print_status()
            TC = rebalance()
            if TC > 0:
                print_status()
        elif not pause_message_printed:
            print('BOT is paused ...')
            pause_message_printed = True  # Set the flag to True after printing the message
        time.sleep(1)  # Adjust the sleep time as needed
    except Exception as e:
        print("Execution Error!", e)
        traceback.print_exc()
        print("Pausing for 10 seconds to review the error...")
        time.sleep(10)  # Pause for 10 seconds to review the error
