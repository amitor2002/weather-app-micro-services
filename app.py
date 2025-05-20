from flask import Flask, render_template, request
from services.weather_service import get_weather_data, get_coordinates  

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    #if there was a post req from the user
    if request.method == 'POST':
        city = request.form.get('city')
        country = request.form.get('country')

        #checks the input 
        if not city and not country:
            error_message = "Please enter at least a city or country name"
            return render_template('index.html', error_message=error_message)
        

        #get the input location coordinates
        latitude, longitude, country, city = get_coordinates(city, country)

        #checks the the output of the coordinates api
        if latitude is None or longitude is None:
            error_message = "Location not found. Try again."
            return render_template('index.html', error_message=error_message)
        
        #get the weather data from the other api
        data = get_weather_data(latitude, longitude)

        #if i really got data from api
        if data:
            #takes the specific data inside
            temperature_today = data['temperature_today']
            humidity_today = data['humidity_today']
            temperature_today_morning = data['temp today morning']
            temperature_today_evening = data['temp today evening']
            humidity_today_morning = data['humid today morning']
            humidity_today_evening = data['humid today evening']
            weekly_forecast = data['weekly_forecast']  # get the full weekly forecast
        else:
            temperature_today = 'Data not available'
            humidity_today = 'Data unknown'
            weekly_forecast = []

        #render all the needed data to html file
        return render_template('index.html', 
                       temperature_today=temperature_today, 
                       humidity_today=humidity_today,
                       temperature_today_morning=temperature_today_morning, 
                       temperature_today_evening=temperature_today_evening,
                       humidity_today_morning=humidity_today_morning, 
                       humidity_today_evening=humidity_today_evening,
                       weekly_forecast=weekly_forecast,
                       city=city, 
                       country=country)

                
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
