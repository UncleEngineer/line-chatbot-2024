from flask import Flask, request, Response
import json
import requests as requests_lib

app = Flask(__name__)

# Replace with your OpenWeather API key
API_KEY = 'Your API KEY Here'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

@app.route('/')
def hello():
    return "Hello World!!", 200

@app.route('/weather')
def get_weather():
    # Get city from request parameters (default to 'London')
    city = request.args.get('city', 'Bangkok')

    # Make API request to OpenWeather
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'  # Display temperature in Celsius
    }
    response = requests_lib.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        weather_data = response.json()
        return Response(json.dumps(weather_data), mimetype='application/json'), 200
    else:
        error_message = {"error": "City not found"}
        return Response(json.dumps(error_message), mimetype='application/json'), 404

if __name__ == '__main__':
    app.run(debug=True,port=5000)
