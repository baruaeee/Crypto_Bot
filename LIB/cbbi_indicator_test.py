import requests
import json, time
#import numpy as np
#from scipy import stats
#import pandas as pd
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

def analyze_confidence(confidence_data):
    """
    Determines market zone based on historical confidence values.
    Returns analysis for only the latest value.
    """
    # Sort timestamps and get latest
    sorted_timestamps = sorted(confidence_data.keys())
    latest_timestamp = sorted_timestamps[-1]

    # Initialize trend as uptrend
    is_uptrend = True

    # Process historical data to determine trend
    for timestamp in sorted_timestamps:
        confidence = confidence_data[timestamp]
        if confidence >= 0.96:
            is_uptrend = False
        elif confidence <= 0.10:
            is_uptrend = True

    # Get final values
    final_confidence = confidence_data[latest_timestamp]

    # Determine zone
    if final_confidence >= 0.96:
        zone = 'top'
    elif final_confidence <= 0.10:
        zone = 'bottom'
    else:
        zone = 'middle_uptrend' if is_uptrend else 'middle_downtrend'
    return zone, final_confidence
    #return {
    #    'confidence': final_confidence,
    #    'zone': zone
    #}

# Example usage
#test_data = {
#    "1309132800": 0.05,    # Bottom
#    "1309219200": 0.15,    # Middle (uptrend)
#    "1309305600": 0.45,    # Middle (uptrend)
#    "1309392000": 0.96,    # Top
#    "1309478400": 0.45,    # Middle (downtrend)
#}

#result = analyze_confidence(read_CBBI())
#print(f"Current confidence: {result['confidence']}")
#print(f"Zone: {result['zone']}")

def modify_ratio():
    # trends are Uptrend, Downtrend, Flat
    trend, confidence = analyze_confidence(read_CBBI())
    # top, bottom, middle_uptrend, middle_downtrend

    if trend == 'bottom':
        r = float(confidence)
    elif trend == 'middle_uptrend' and 0.10 < float(confidence) <= 0.70:
        r = 0.05
    elif trend == 'middle_uptrend' and 0.70 < float(confidence) <= 0.80:
        r = 0.08
    elif trend == 'middle_uptrend' and 0.80 < float(confidence) <= 0.90:
        r = 0.10
    elif trend == 'middle_uptrend' and 0.90 < float(confidence) < 0.96:
        r = float(confidence) - 0.5
    elif trend == 'top':
        r = 0.96
    elif trend == 'middle_downtrend' and float(confidence) > 0.20:
        r = 0.96
    elif trend == 'middle_downtrend' and float(confidence) <= 0.20:
        r = 0.80
    else:
        r = float(confidence)
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Ratio: {round(r, 4)}, Trend: {trend}, Conf: {confidence} -- {current_time}", end='\r')
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

#modify_ratio()

#result = analyze_trend(read_CBBI())
#print(result)
