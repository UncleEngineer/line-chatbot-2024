import requests

API_URL = "YOUR LOCALHOST PORT 3000 RUNNIGN FLOWISE"
headers = {"Authorization": "Bearer YOUR FLOWISE API KEY"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()
    
output = query({
    "question": "โรเบิรต์คือใคร",
})

print(output['text'])