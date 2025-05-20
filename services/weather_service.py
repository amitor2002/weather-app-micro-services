#to work with openmeteo methodologies
import openmeteo_requests
#for the cache option
import requests_cache
#for the retry if api couldnt find at first
from retry_requests import retry
import requests
import datetime


def get_weather_data(latitude, longitude):

    #cached previous lookups up to a 1000 sec
    #when u call "request_cache", the cache_session listen
    #to all calls to api from the current session
    cache_session = requests_cache.CachedSession('.cache', expire_after=1000)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client()

    #api
    url = "https://api.open-meteo.com/v1/forecast"

    #dict of needed parameters
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m"],
        "hourly": ["temperature_2m", "relative_humidity_2m"],
        "timezone": "auto"
    }

    #get list of responses from the weather api via the parameters
    responses = openmeteo.weather_api(url, params=params)   
    #only the first option in case of multiple
    response = responses[0] 
    
    # getting today's data using openmeteo methods
    current = response.Current()
    temperature_today = current.Variables(0).Value()
    humidity_today = current.Variables(1).Value()

    # Getting hourly data
    hourly = response.Hourly()
    temperature_hourly = hourly.Variables(0).ValuesAsNumpy()
    humidity_hourly = hourly.Variables(1).ValuesAsNumpy()


    #temp for day and night for today
    temperature_morning_today = temperature_hourly[8]
    temperature_evening_today = temperature_hourly[20]
    humidity_morning_today = humidity_hourly[8]
    humidity_evening_today = humidity_hourly[20]
        
    #hours for morning-night
    morning_hour = 8
    evening_hour = 20

    #number of days of the data we got
    num_hours = len(temperature_hourly)
    #we got 24 hours a day
    num_days = num_hours // 24


    # constructing the weekly forecast
    weekly_forecast = []
    #today's date
    today = datetime.date.today()
    for i in range(num_days):

        #tomorrow's date
        day_date = today + datetime.timedelta(days=i+1)

        #calculate the next day in the week
        #starting from the next day from today 
        morning_index = i * 24 + morning_hour
        evening_index = i * 24 + evening_hour

        weekly_forecast.append({
            #the indexes in the list of the temp/humidity are ordered like:
            #24 * 7 (24 hours a day 7 days), so this is how we access the data
            "day": day_date.strftime("%d-%m-%y"),
            "temp_morning": temperature_hourly[morning_index],
            "temp_evening": temperature_hourly[evening_index],
            "humidity_morning": humidity_hourly[morning_index],
            "humidity_evening": humidity_hourly[evening_index],
        })

    return {
        "temperature_today": temperature_today,
        "humidity_today": humidity_today,
        "temp today morning": temperature_morning_today,
        "temp today evening": temperature_evening_today,
        "humid today morning": humidity_morning_today,
        "humid today evening": humidity_evening_today,
        "weekly_forecast": weekly_forecast  
    }


def get_coordinates(city, country):
    query = f"{city}, {country}"
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&accept-language=en&addressdetails=1&limit=1"
    
    response = requests.get(url, headers={'User-Agent': 'weather-app'})
    data = response.json()
    
    if data:
        location = data[0]
        latitude = float(location['lat'])
        longitude = float(location['lon'])

        #gets the country, and city if the user entered only city name
        country_name = location.get('address', {}).get('country', None)

        if not country_name:
            # if no country was not found in 'address', try to extract from 'display_name'
            display_name = location.get('display_name', '')
            # looking for the last part of the display_name (which should be the country)
            country_name = display_name.split(',')[-1].strip()
        
        return location['lat'], location['lon'], city, country_name
    else:
        return None, None, None, None

