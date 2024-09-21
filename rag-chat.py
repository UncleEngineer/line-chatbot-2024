from flask import Flask, request
import json
import requests as requests_lib
import os


app = Flask(__name__)

Line_Access_TOKEN = os.getenv('LINE_ACCESS_TOKEN In Your ENV')

# def get_openai_response(user_message):

#     payload = client.chat.completions.create(
#         model = "gpt-4o",
#         messages=[
#             {"role":"system", "content": "You are a helpful assistant, YOU MUST RESPOND IN THAI"},
#             {"role": "user", "content": user_message}
#         ]
#     )

#     response = payload.choices[0].message.content
#     return response

FLOWISE_API_URL = "YOUR LOCALHOST PORT 3000 RUNNIGN FLOWISE"
flowise_headers = {"Authorization": "Bearer YOUR FLOWISE API KEY"}

def rag_query(payload):
    response = requests_lib.post(FLOWISE_API_URL, headers=flowise_headers, json=payload)
    return response.json()
    
# output = query({
#     "question": "Hey, how are you?",
# })


@app.route('/webhook', methods=['POST','GET'])
def webhook():
    if request.method == "POST":  # User send message to LINE (POST)
        req = request.json
        if 'events' in req:
            for event in req['events']:
                if event['type'] == 'message' and event['message']['type'] == 'text':
                    user_message = event['message']['text']

                    output = rag_query({
                        "question" : user_message,
                    })
        
                    # response_message = get_openai_response(user_message)
                    response_message = output['text']

                    Reply_token = event['replyToken']
                    ReplyMessage(Reply_token,response_message, Line_Access_TOKEN)
        return "POST",200
    elif request.method == "GET":
        return "GET",200

def ReplyMessage(Reply_token, TextMessage, Line_Access_TOKEN):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'

    Authorization = 'Bearer {}'.format(Line_Access_TOKEN)
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization' : Authorization
    }

    data = {
        "replyToken": Reply_token,
        "messages":[{
            "type":"text",
            "text":TextMessage
        }]
    }
    data = json.dumps(data) # dict -> json
    full_request = requests_lib.post(LINE_API, headers=headers, data=data)
    return full_request.status_code


if __name__ == "__main__":
    app.run(debug=True, port=5000)