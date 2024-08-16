import os
import songline

NOTIFY_TOKEN = os.environ.get('line-noti-token')

# print(NOTIFY_TOKEN)
messenger = songline.Sendline(NOTIFY_TOKEN)

'''
messenger.sendtext('songline by uncle engineer')
text_message = 'ราคาหุ้น xxx กี่ yyy บาท'
messenger.sendtext(text_message)
'''

messenger.sendimage("https://i.pinimg.com/736x/1a/fd/aa/1afdaa0a8c9a3b3e2e015bf1bb637008.jpg")