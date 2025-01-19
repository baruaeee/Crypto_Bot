from binance.client import Client
from datetime import datetime
from decimal import Decimal
import time
import os
import pandas as pd


import getpass
# ----Get the input securely----
#api_key = getpass.getpass("Enter your API key: ")
#api_secret = getpass.getpass("Enter your secret: ")


api_key = '1JkjQbzKnRhvUqf2zzuv8Tb25UR31Nf87RwTA5XtTRzpw8lTk9UEvY7cnTh04u9T'
api_secret = 'GnO6aPWkwCzGktTGSpInpGUDTU9wGXF7RI5yOA9siEtQvGnTpjRZRaGw8zd5b9Nt'


# ----initialize the Binanace client (testnet argument is not necessary in actual binance)----
client = Client(api_key, api_secret, testnet=True)
#client = Client(api_key, api_secret)

def read_price(crypto):
    # client.get_ticker(symbol=crypto) will get a dictionary data from which I only take 'lastPrice'
    return client.get_ticker(symbol=crypto)['lastPrice']


def read_param(cn, bcn, x):
    df = pd.read_csv('conf.csv', sep=', ', engine='python',skipinitialspace=True)
    row = df.index[df['pair'] == (cn + bcn)].tolist()[0]
    data = df.at[row, x]
    return data

def Reb(coin, base_coin):
    qty_min = Decimal(str(client.get_symbol_info(coin + base_coin)['filters'][1]['minQty'])).normalize()
    #print(Decimal(str(info)).normalize())
    #print(Decimal(info).normalized())
    buy_frac = read_param(coin, base_coin, 'buy_frac')
    sell_frac = read_param(coin, base_coin, 'sell_frac')
    coin_dist = read_param(coin, base_coin, 'coin_dist')
    pair_min = read_param(coin, base_coin, 'pair_min')
    pair_max = read_param(coin, base_coin, 'pair_max')
    div = read_param(coin, base_coin, 'div')
    #crypto_frac_calc = coin_dist
    #print(coin, coin_dist)

    if str(qty_min).isdigit():
        qty_rnd = 0
    else:
        qty_rnd = len(str(qty_min).split('.')[1])
    count = 0
    #from binance.client import Client
    #client = Client(key, secret, testnet=True)
    base = float(client.get_asset_balance(asset=base_coin)['free'])
    if base_coin != 'USDT':
        base_USDT = float(read_price(base_coin+'USDT'))
        base_USD_Balance = base_USDT*base
    else:
        base_USD_Balance = base
    crypto = float(client.get_asset_balance(asset=coin)['free'])
    crypto_USDT = float(read_price(coin+'USDT'))
    crypto_USD_Balance = crypto_USDT*crypto

    # get coin-pair fraction
    if coin_dist!= 0:
        crypto_frac_calc = coin_dist
        #print(coin, crypto_frac_calc)
    else:
        coin_pair = float(read_price(coin+base_coin))
        if ((0.1 - (0.8*(coin_pair-pair_max)/(pair_max - pair_min)))/div) > 0.96:
            crypto_frac_calc = 0.96
        elif ((0.1 - (0.8*(coin_pair-pair_max)/(pair_max - pair_min)))/div) < 0.04:
            crypto_frac_calc = 0.04
        else:
            crypto_frac_calc = (0.1 - (0.8*(coin_pair-pair_max)/(pair_max - pair_min)))/div
    base_frac_calc = 1-crypto_frac_calc


	# Adjustment/Rebalance ammounts (cryptoBTC pair)
    crypto_adj = ((crypto_frac_calc*(crypto_USD_Balance+base_USD_Balance)) - crypto_USD_Balance)/crypto_USDT
    crypto_trade = round(abs(crypto_adj), qty_rnd)
    if crypto == 0:
        trade_percent = 100
    else:
        trade_percent = crypto_trade*100/crypto
    if crypto_adj < 0 and trade_percent >= sell_frac:
        client.create_order(symbol = coin+base_coin, side = 'SELL', type='MARKET', quantity=float(crypto_trade))
        count = count+1
    elif crypto_adj > 0 and trade_percent >= buy_frac:
        client.create_order(symbol = coin+base_coin, side = 'BUY', type='MARKET', quantity=float(crypto_trade))
        count = count+1
    return count

def rebalance():
    trade_count = 0
    # Reb(coin, base_coin, buy_frac, sell_frac, coin_dist=0, pair_min = 0, pair_max = 0, div = 0)
    while trade_count == 0:
        if trade_count == 0:
            trade_count = trade_count+Reb('BNB', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('FTM', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('SEI', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('SOL', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('NEO', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('FIL', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('LINK', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('AVAX', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('MATIC', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('ADA', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('PAXG', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('XRP', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('ETH', 'BTC')
        if trade_count == 0:
            trade_count = trade_count+Reb('SOL', 'BTC')
    return trade_count

# Print status
def prnt_status():
    XRP = float(client.get_asset_balance(asset='XRP')['free'])
    ETH = float(client.get_asset_balance(asset='ETH')['free'])
    SOL = float(client.get_asset_balance(asset='SOL')['free'])
    BTC = float(client.get_asset_balance(asset='BTC')['free'])
    PAXG = float(client.get_asset_balance(asset='PAXG')['free'])
    ADA = float(client.get_asset_balance(asset='ADA')['free'])
    MATIC = float(client.get_asset_balance(asset='MATIC')['free'])
    AVAX = float(client.get_asset_balance(asset='AVAX')['free'])
    LINK = float(client.get_asset_balance(asset='LINK')['free'])
    FIL = float(client.get_asset_balance(asset='FIL')['free'])
    NEO = float(client.get_asset_balance(asset='NEO')['free'])
    SEI = float(client.get_asset_balance(asset='SEI')['free'])
    FTM = float(client.get_asset_balance(asset='FTM')['free'])
    BNB = float(client.get_asset_balance(asset='BNB')['free'])
    USDT = float(client.get_asset_balance(asset='USDT')['free'])

    BTCUSDT = float(read_price('BTCUSDT'))
    SOLUSDT = float(read_price('SOLUSDT'))
    ETHUSDT = float(read_price('ETHUSDT'))
    XRPUSDT = float(read_price('XRPUSDT'))
    PAXGUSDT = float(read_price('PAXGUSDT'))
    ADAUSDT = float(read_price('ADAUSDT'))
    MATICUSDT = float(read_price('MATICUSDT'))
    AVAXUSDT = float(read_price('AVAXUSDT'))
    LINKUSDT = float(read_price('LINKUSDT'))
    FILUSDT = float(read_price('FILUSDT'))
    NEOUSDT = float(read_price('NEOUSDT'))
    SEIUSDT = float(read_price('SEIUSDT'))
    FTMUSDT = float(read_price('FTMUSDT'))
    BNBUSDT = float(read_price('BNBUSDT'))

    BTC_balance = BTC*BTCUSDT
    SOL_balance = SOL*SOLUSDT
    ETH_balance = ETH*ETHUSDT
    XRP_balance = XRP*XRPUSDT
    PAXG_balance = PAXG*PAXGUSDT
    ADA_balance = ADAUSDT*ADA
    MATIC_balance = MATICUSDT*MATIC
    AVAX_balance = AVAXUSDT*AVAX
    LINK_balance = LINKUSDT*LINK
    FIL_balance = FILUSDT*FIL
    NEO_balance = NEOUSDT*NEO
    SEI_balance = SEIUSDT*SEI
    FTM_balance = FTMUSDT*FTM
    BNB_balance = BNBUSDT*BNB

    Balance_sum = BTC_balance + SOL_balance + ETH_balance + XRP_balance + PAXG_balance + ADA_balance + MATIC_balance + AVAX_balance + LINK_balance + FIL_balance + NEO_balance + SEI_balance + FTM_balance + BNB_balance + USDT

    BTC_frac = BTC_balance/Balance_sum
    SOL_frac = SOL_balance/Balance_sum
    ETH_frac = ETH_balance/Balance_sum
    XRP_frac = XRP_balance/Balance_sum
    PAXG_frac = PAXG_balance/Balance_sum
    ADA_frac = ADA_balance/Balance_sum
    MATIC_frac = MATIC_balance/Balance_sum
    AVAX_frac = AVAX_balance/Balance_sum
    LINK_frac = LINK_balance/Balance_sum
    FIL_frac = FIL_balance/Balance_sum
    NEO_frac = NEO_balance/Balance_sum
    SEI_frac = SEI_balance/Balance_sum
    FTM_frac = FTM_balance/Balance_sum
    BNB_frac = BNB_balance/Balance_sum
    USDT_frac = USDT/Balance_sum

    #print("\t\t\t=========\n")
    now = datetime.now()

    print("----"+ now.strftime("%d/%m/%Y %H:%M:%S") + "----\n" +
          "BTC Balance:\t" + str(round(BTC,4)) + "\t\t$" + str(round(BTC_balance, 4))+ "\t" + str(round(BTC_frac*100, 2))+"%"+"\n"+
          "SOL Balance:\t" + str(round(SOL, 4)) + "\t\t$" + str(round(SOL_balance, 4))+ "\t" + str(round(SOL_frac*100, 2))+"%"+"\n" +
          "ETH Balance:\t" + str(round(ETH, 4)) + "\t\t$" + str(round(ETH_balance, 4))+ "\t" + str(round(ETH_frac*100, 2))+"%"+ "\n" +
          "XRP Balance:\t" + str(round(XRP, 4)) + "\t\t$" + str(round(XRP_balance, 4))+ "\t" + str(round(XRP_frac*100, 2))+"%"+ "\n" +
          "PAXG Balance:\t" + str(round(PAXG, 4)) + "\t\t$" + str(round(PAXG_balance, 4))+ "\t" + str(round(PAXG_frac*100, 2))+"%"+ "\n" +
          "ADA Balance:\t" + str(round(ADA, 4)) + "\t\t$" + str(round(ADA_balance, 4))+ "\t" + str(round(ADA_frac*100, 2))+"%"+ "\n" +
          "MATIC Balance:\t" + str(round(MATIC, 4)) + "\t\t$" + str(round(MATIC_balance, 4))+ "\t" + str(round(MATIC_frac*100, 2))+"%"+ "\n" +
          "AVAX Balance:\t" + str(round(AVAX, 4)) + "\t\t$" + str(round(AVAX_balance, 4))+ "\t" + str(round(AVAX_frac*100, 2))+"%"+ "\n" +
          "LINK Balance:\t" + str(round(LINK, 4)) + "\t\t$" + str(round(LINK_balance, 4))+ "\t" + str(round(LINK_frac*100, 2))+"%"+ "\n" +
          "FIL Balance:\t" + str(round(FIL, 4)) + "\t\t$" + str(round(FIL_balance, 4))+ "\t" + str(round(FIL_frac*100, 2))+"%"+ "\n" +
          "NEO Balance:\t" + str(round(NEO, 4)) + "\t\t$" + str(round(NEO_balance, 4))+ "\t" + str(round(NEO_frac*100, 2))+"%"+ "\n" +
          "SEI Balance:\t" + str(round(SEI, 4)) + "\t\t$" + str(round(SEI_balance, 4))+ "\t" + str(round(SEI_frac*100, 2))+"%"+ "\n" +
          "FTM Balance:\t" + str(round(FTM, 4)) + "\t\t$" + str(round(FTM_balance, 4))+ "\t" + str(round(FTM_frac*100, 2))+"%"+ "\n" +
          "BNB Balance:\t" + str(round(BNB, 4)) + "\t\t$" + str(round(BNB_balance, 4))+ "\t" + str(round(BNB_frac*100, 2))+"%"+ "\n" +
          "USDT Balance:\t" + str(round(USDT, 3)) + "\t\t$" + str(round(USDT, 3))+ "\t" + str(round(USDT_frac*100, 2))+"%"+ "\n")
    print("USD Total:\t", str(Balance_sum), "\n")

    #print("\t\t\t=========\n")

    '''
    print("Distribution:\nBTC\t:"+str(round(BTC_frac*100, 2))+"%" "\nSOL\t:"+str(round(SOL_frac*100, 2))+"%"+
          "\nETH\t:" + str(round(ETH_frac*100, 2)) + "%" + "\nXRP\t:" + str(round(XRP_frac*100, 2)) + "%"
                                                + "\nPAXG\t:" + str(round(PAXG_frac*100, 2)) + "%\n")
    '''
#prnt_status()

while True:
    try:
        #os.system('clear')
        print('BOT is running ...')
        prnt_status()
        while True:
            TC = rebalance()
            if TC > 0:
                prnt_status()
                #time.sleep(2)

    except Exception as e:
        print("Execution Error!", e)
        print("Retrying ...")
