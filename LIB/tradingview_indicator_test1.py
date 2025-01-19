import requests
import json, time
import pandas as pd
from binance.client import Client
import numpy as np
from datetime import datetime




# get Fear and Greed data
def fng():
    url = "https://api.alternative.me/fng/"
    response_API = requests.get(url)
    data = response_API.text
    parse_json = json.loads(data)
    fng = int(parse_json['data'][0]['value'])
    return fng



# Function to fetch historical Kline data from Binance
def get_historical_klines(symbol, interval, start_time):
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': start_time,
        'limit': 1000  # Maximum number of data points
    }
    response = requests.get(url, params=params)
    return response.json()

# Function to calculate RSI
def calculate_rsi(prices, period=14):
    delta = np.diff(prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = np.mean(gain[:period])
    avg_loss = np.mean(loss[:period])

    rsi = np.zeros_like(prices)
    rsi[:period] = 100 - (100 / (1 + (avg_gain / avg_loss)))
    #rsi[:period] = 100 / (1 + (avg_gain / avg_loss))

    for i in range(period, len(prices)):
        avg_gain = (avg_gain * (period - 1) + gain[i - 1]) / period
        avg_loss = (avg_loss * (period - 1) + loss[i - 1]) / period
        rs = avg_gain / avg_loss
        rsi[i] = 100 - (100 / (1 + rs))
        #rsi[i] = 100 - (100 / (1 + rs))

    return rsi

# Function to calculate Stochastic RSI
def calculate_stochastic_rsi(rsi, period=14):
    stoch_rsi = (rsi - np.min(rsi[-period:])) / (np.max(rsi[-period:]) - np.min(rsi[-period:]))
    return stoch_rsi

# Function to calculate %K and %D lines
def calculate_k_d(stoch_rsi, k_period=3, d_period=3):
    k_line = pd.Series(stoch_rsi).rolling(window=k_period).mean().to_numpy()
    d_line = pd.Series(k_line).rolling(window=d_period).mean().to_numpy()
    return k_line, d_line

# Main function
def stock_rsi():
    #symbol = 'BTCUSDT'
    symbol = 'PAXGBTC'
    interval = '1w'  # Weekly interval
    start_time = '1577836800000'  # Start time in milliseconds (January 1, 2020)

    # Fetch historical Kline data
    klines = get_historical_klines(symbol, interval, start_time)

    # Extract closing prices
    closing_prices = [1/float(kline[4]) for kline in klines]
    #closing_prices = [float(kline[4]) for kline in klines]

    # Calculate RSI
    rsi = calculate_rsi(np.array(closing_prices))

    # Calculate Stochastic RSI
    stoch_rsi = calculate_stochastic_rsi(rsi)

    # Calculate %K and %D lines
    k_line, d_line = calculate_k_d(stoch_rsi)
    # print(k_line)

    strsi = stoch_rsi[-1]
    k = k_line[-1]
    d = d_line[-1]

    return strsi , k, d

def modify_ratio():
    fg = fng()/100
    #s, k, d = stock_rsi()
    s, d, k = stock_rsi()
    #print(k, d)
    #s2, k2, d2 = stock_rsi()
    #s = 100 - s2
    #k = 100 - k2
    #d = 100 - d2
    k1 = 0.7*k + 0.3*fg
    d1 = 0.75*k + 0.25*fg
    #print(k1, d1)
    if k1<0.20:
        r = 0.05
    elif k1>d1 and 0.25<k1<0.75:
        r = 0.8*s + 0.2*fg
    elif k1>d1 and 0.75<k1<0.80:
        r = 0.75
    elif k1>d1 and 0.80<k1:
        r = 0.85
    elif k1<d1 and 0.80<k1:
        r = 0.85
    elif k1<d1 and 0.90<k1:
        r = 0.90
    elif k1<d1 and 0.80>k1:
        r = 0.85
    elif k1<d1 and 0.25<k1<0.75:
        r = 0.8
    else:
        r = 0.5*s + 0.5*fg
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Ratio: {round(r, 4)}, FnG: {fng()} -- {current_time}", end='\r')
    #print(f"Ratio: {round(r, 4)}, FnG: {fng()} -- {current_time}")
    with open('conf1.csv', 'r+') as file:
        lines = file.readlines()
        new_lines = []
        file.seek(0)
        file.truncate()
        for line in lines:
            if 'PAXGBTC' in line:
                params = line.strip().split(', ')
                params[3] = str(round(r, 4))
                line = ', '.join(params)+'\n'
                #print(line)
            new_lines.append(line)
        #print(lines)
        file.writelines(new_lines)
        #print(lines)
        file.close()
#while True:
#    modify_ratio()
#    time.sleep(10)

