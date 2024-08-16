# Line notify
import os
import requests

NOTIFY_TOKEN = os.environ.get('line-noti-token')

# print(NOTIFY_TOKEN)

def notify(message):
    LINE_NOTIFY_API = 'https://notify-api.line.me/api/notify'
    headers = {'content-type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer ' + NOTIFY_TOKEN}
    
    return requests.post(LINE_NOTIFY_API, headers=headers, data=message)

msg1 = {'message': "hello line notify from uncle engineer"}
msg2 = {'message': "hello hello"}
msg3 = {'message': "สวัสดีครับ"}
# notify(msg3)

monday_url = "https://stickershop.line-scdn.net/stickershop/v1/product/13558684/LINEStorePC/main.png?v=2"
msg4 = {'message': "สวัสดีวันจันทร์", 'imageThumbnail': monday_url, 'imageFullsize': monday_url}
# notify(msg4)

msg5 = {'message':"test sticker",'stickerPackageId': 6136, 'stickerId': 10551378}
notify(msg5)
