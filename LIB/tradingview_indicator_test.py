import requests
import json, time
import numpy as np
from scipy import stats
import pandas as pd
from datetime import datetime

def read_CBBI():
    # URL of the JSON data
    url = "https://colintalkscrypto.com/cbbi/data/latest.json"

    # Set headers to request JSON format and mimic a browser
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }

    # Send a GET request to the URL with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        data = response.text
        parse_json = json.loads(data)
        return parse_json.get("Confidence")  # Print the JSON data
    else:
        print(f"Failed to retrieve data: {response.status_code}")

#print(read_CBBI())

def analyze_trend(data_dict):
    # Convert Unix timestamps to datetime index
    df = pd.DataFrame(list(data_dict.items()), columns=['timestamp', 'value'])

    # Explicitly convert timestamp to numeric type before to_datetime
    df['timestamp'] = pd.to_numeric(df['timestamp'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

    df.set_index('datetime', inplace=True)

    # Resample to weekly data (last value of each week)
    weekly_data = df['value'].resample('W').last()

    # Get last 4 weeks of data for recent trend
    recent_weeks = weekly_data.tail(5)

    # Perform linear regression on recent weekly data
    x = np.arange(len(recent_weeks))
    y = recent_weeks.values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # Determine trend
    if slope > 0:
        trend = "Uptrend"
    elif slope < 0:
        trend = "Downtrend"
    else:
        trend = "Flat"

    # Calculate percentage change
    percent_change = ((recent_weeks.iloc[-1] - recent_weeks.iloc[0]) / recent_weeks.iloc[0]) * 100

    # Get the absolute last value from the original dataset
    last_value = df['value'].iloc[-1]
    #print(type(last_value), type(trend))

    return trend, last_value

#    return {
#        'trend': trend,
#        'last_value': last_value
#        'slope': slope,
#        'percent_change': percent_change,
#        'weekly_values': recent_weeks.to_dict(),
#        'r_squared': r_value**2
#        }

def modify_ratio():
    # trends are Uptrend, Downtrend, Flat
    trend, confidence = analyze_trend(read_CBBI())

    if trend == 'Downtrend' and float(confidence) < 0.10:
        r = float(confidence)
    elif trend == 'Uptrend' and float(confidence) < 0.10:
        r = 0.05
    elif trend == 'Uptrend' and 0.11 < float(confidence) < 0.90:
        r = 0.05
    elif trend == 'Uptrend' and 0.91 < float(confidence) <= 0.96:
        r = float(confidence)
    elif trend == 'Uptrend' and float(confidence) > 0.96:
        r = 0.96
    elif trend == 'Downtrend' and float(confidence) > 0.96:
        r = 0.96
    elif trend == 'Downtrend' and 0.11 < float(confidence) < 0.95:
        r = 0.96
    else:
        r = float(confidence)
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Ratio: {round(r, 4)}, Tr: {trend},Conf.: {confidence} -- {current_time}", end='\r')
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

modify_ratio()

#result = analyze_trend(read_CBBI())
#print(result)
