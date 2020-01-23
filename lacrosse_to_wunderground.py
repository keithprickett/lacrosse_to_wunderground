"""
Downloads weather data from La Crosse Cloud System from your personal
weather station and uploads it to Wunderground via the wunderground/weather
personal weather station API.
"""

import sys
import time
import requests
import json
import datetime
from lacrosse_weather.lacrosse import lacrosse_login, lacrosse_get_locations, lacrosse_get_devices, lacrosse_get_weather_data
from wunderground_uploader.uploader import wunderground_upload_data_point


email = 'YOUR LA CROSSE VIEW ACCOUNT EMAIL'
password = 'YOUR LA CROSSE VIEW ACCOUNT PW'
station_id = 'YOUR WUNDERGROUND PWS STATION ID'
station_key = 'YOUR WUNDERGROUND PWS STATION KEY'
api_key = 'YOUR WUNDERGROUND API KEY'


def wunderground_get_utc_of_latest(station_id, api_key):
    try:
        r = requests.request('GET', 'https://api.weather.com/v2/pws/observations/current?stationId={}&format=json&units=e&apiKey={}'.format(station_id, api_key))
        j = json.loads(r.content.decode('utf-8'))
        ts = datetime.datetime.strptime(j['observations'][0]['obsTimeUtc'], "%Y-%m-%dT%H:%M:%S%z").timestamp()
    except Exception:
        ts = 0
        print("Warning: Didn't get latest observation time, loading from time 0")
    return int(ts)


def celsius_to_fahrenheit(celsius):
    return (celsius * (9 / 5) ) + 32


def kilometers_per_hour_to_miles_per_hour(kilometers_per_hour):
    return kilometers_per_hour / 1.609


def push_all_since_timestamp_temperature_to_wunderground(w, old_utc_timestamp):
    for temp_data, humidity_data in zip(w['Temperature']['values'], w['Humidity']['values']):
        utc_timestamp = temp_data['u']
        if utc_timestamp > old_utc_timestamp:
            weather_data = dict(
                tempf=celsius_to_fahrenheit(temp_data['s']),
                humidity=humidity_data['s']
            )
            wunderground_upload_data_point(station_id, station_key, weather_data, utc_timestamp)
            time.sleep(2.5)


def push_all_since_timestamp_wind_to_wunderground(w, old_utc_timestamp):
        for wind_data in w['WindSpeed']['values']:
            utc_timestamp = wind_data['u']
            if utc_timestamp > old_utc_timestamp:
                weather_data = dict(
                       windspeedmph=kilometers_per_hour_to_miles_per_hour(wind_data['s'])
                )
                wunderground_upload_data_point(station_id, station_key, weather_data, utc_timestamp)
                time.sleep(2.5)

if __name__ == '__main__':
    try:
        old_utc_timestamp = int(sys.argv[1])
    except Exception:
        old_utc_timestamp = wunderground_get_utc_of_latest(station_id, api_key)

    token = lacrosse_login(email, password)
    locations = lacrosse_get_locations(token)
    devices = lacrosse_get_devices(token, locations)
    new_timestamp = old_utc_timestamp
    try:
        for device in devices:
            # TODO Will need updated credentials if we do long operations
            # Your 'device_name' is likely different than 'temperature'
            # replace this name with something that has an external "Temperature"
            # sensor
            # doing the following can show you the name here:
            #  print(device['device_name'])
            # Same below with 'wind'
            if device['device_name'] == 'temperature':
                w = lacrosse_get_weather_data(token, device)
                push_all_since_timestamp_temperature_to_wunderground(w, old_utc_timestamp)
                new_timestamp = w['Temperature']['values'][-1]['u']

        # Do this twice, as long pushes agove may cause credentials to expire
        token = lacrosse_login(email, password)
        locations = lacrosse_get_locations(token)
        devices = lacrosse_get_devices(token, locations)
        for device in devices:
            if device['device_name'] == 'wind':
                w = lacrosse_get_weather_data(token, device)
                push_all_since_timestamp_wind_to_wunderground(w, old_utc_timestamp)
    except Exception:
        # Ignore all errors, just retry again later with your automation
        pass

    # Usage:
    # New timestamp is printed as output, pipe it to a file and use that file
    # as input the next time the script is run. Set the file the first time
    # manually
    #
    # i.e. python3 lacrosse_to_wunderground.py `cat weather_ts` > weather_ts
    print(new_timestamp)
