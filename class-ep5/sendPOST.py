import requests
import json

# usl to send post 
url = "http://localhost:5000/methods"
data = {
    "message": "Hello, Flask!"
}

response = requests.post(url, json=data)

print(f"Status Code: {response.status_code} ")
print(f"Response Body: {response.text} ")