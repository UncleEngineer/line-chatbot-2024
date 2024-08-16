import requests
import os
import songline

openweather_api = os.environ.get('openweather-api')
line_noti_token = os.environ.get('line-noti-token')
messenger = songline.Sendline(line_noti_token)

# print(openweather_api)

url = 'http://api.openweathermap.org/data/2.5/weather?q=bangkok&appid={}&units=metric'.format(openweather_api)

response = requests.get(url)
# print(response)
data = response.json()
print(data)

humidity = data['main']['humidity']
pressure = data['main']['pressure']
wind = data['wind']['speed']
description = data['weather'][0]['description']
temp = data['main']['temp']

output = (
    f'\nTemperature: {temp} °C\n'
    f'Wind: {wind}\n'
    f'Pressure: {pressure}\n'
    f'Humid: {humidity}\n'
    f'Description: {description}'
)
# print(output)
messenger.sendtext(output)

if temp > 30:
    messenger.sendimage('https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgve0MrJS7A1bOn8f4rNhbU29O4JhZUbglCTIb0iiUSM4h-AUStwnMAM_zkDq9rF3baCkiMMMRvMmxH5bjhcd5UcG69JTNd63oVQw0AukCklkzvB2PPpP0VUwSt-aoao8bV50sw4es6TCwi/s180-c/tenki_hare_otoko.png')
if 'cloud' in description:
    messenger.sendimage('https://www.rochesterfirst.com/wp-content/uploads/sites/66/2021/04/black-rain-abstract-dark-power-1-1.jpg?w=900')