import datetime
import errno
import os
import sys
import logging
import tempfile
from argparse import ArgumentParser
import time

# import function / api
from openai import OpenAI
from rembg import remove
from searchapi import search_zenserp
from gdriveapi import upload_to_gdrive


from flask import Flask, request, abort, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.models import (
    UnknownEvent
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)

from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    FileMessageContent,
)

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    PushMessageRequest,
    ApiException,
    Emoji,
    TextMessage,
    ImageMessage,
    QuickReply,
    QuickReplyItem,
    PostbackAction,
    DatetimePickerAction,
    CameraAction,
    CameraRollAction,
    LocationAction,
    ErrorResponse,
    MessageAction,
    URIAction,
    ShowLoadingAnimationRequest,
)

from linebot.v3.insight import (
    ApiClient as InsightClient,
    Insight
)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.INFO)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('line_channel_secret', None)
channel_access_token = os.getenv('line_access_token', None)
if channel_secret is None or channel_access_token is None:
    print('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

handler = WebhookHandler(channel_secret)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

configuration = Configuration(
    access_token=channel_access_token
)
userid = "U7dc185db338241c31bc6714fcbbb1422"
OCR_Mode = False

def get_quick_reply_items():
    return [
        QuickReplyItem(
            action=MessageAction(label="info", text="Features")
        ),
        QuickReplyItem(
            action=MessageAction(label="OCR", text="OCR Mode")
        ),
        QuickReplyItem(
            action=MessageAction(label="ค่าใช้จ่ายรายวัน", text="Today Expenses")
        ),
        QuickReplyItem(
            action=MessageAction(label="ค่าใช้จ่ายรายเดือน", text="Monthy Expenses")
        )
    ]

def get_openai_response(user_message):

    payload = client.chat.completions.create(
        model="gpt-4o-mini",  # เลือก model ได้จาก https://platform.openai.com/docs/models
        messages=[
            {"role": "system", "content": "You must respond to the user in Thai."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=300,
        temperature=0.7,
        presence_penalty=0,
        frequency_penalty=0
    )

    response = payload.choices[0].message.content.strip()
    return response

# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except ApiException as e:
        app.logger.warn("Got exception from LINE Messaging API: %s\n" % e.body)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    text = event.message.text
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if text.lower().startswith("search "):
            # Zenserp API search here # fix the split
            search_query = event.message.text[7:]
            search_results = search_zenserp(search_query)
            
            line_bot_api.show_loading_animation(ShowLoadingAnimationRequest(
            chat_id=userid,
            loading_seconds=10))
            # -----------------------#
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token = event.reply_token,
                    messages=[
                        TextMessage(text=search_results,
                        quick_reply=QuickReply(items=get_quick_reply_items())
                        )
                    ]
                )
            )

        elif text == 'Features':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text = '1. ส่งรูปภาพ เพื่อทำการ Remove Background หรือ OCR\n2. Upload file ขึ้น Google Drive\n3. คุยกับ ChatGPT หรือ Search หาข้อมูลด้วย ZenSerp API',
                        quick_reply=QuickReply(items=get_quick_reply_items())
                        )
                    ]
        )
    )   

        elif text == 'Today Expenses' :
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='Displaying Today Expenses',
                        quick_reply=QuickReply(items=get_quick_reply_items())
                        )
                    ]
        )
    )

        elif text == 'Monthy Expenses' :
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='Displaying Monthy Expenses',
                        quick_reply=QuickReply(items=get_quick_reply_items())
                        )
                    ]
        )
    )
        elif text == 'OCR Mode' :
            global OCR_Mode 
            OCR_Mode = True
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='ส่งรูปภาพสลิปมาได้เลยครับ',
                        )
                    ]
        )
    )
        else: # changed into talking with openai instead of using searchapi
            line_bot_api.show_loading_animation(ShowLoadingAnimationRequest(
                    chat_id=userid,
                    loading_seconds=10))
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text=f'ChatGPT: {get_openai_response(text)}',
                        quick_reply=QuickReply(items=get_quick_reply_items())
                        )
                    ]
                )
            )

@handler.add(MessageEvent, message=(ImageMessageContent))
def handle_image_message(event):
    if isinstance(event.message, ImageMessageContent):
        ext = 'png'
    else:
        return
        
    with ApiClient(configuration) as api_client:
        line_bot_blob_api = MessagingApiBlob(api_client)


        # Get the content of the image message
        message_content = line_bot_blob_api.get_message_content(message_id=event.message.id)
        
        # Save the image temporarily
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='img-', delete=False) as tf:
            tf.write(message_content)
            tempfile_path = tf.name
        
    if OCR_Mode:
        pass
    else:
        # Output paths for rembg processing
        output_path = tempfile_path + '-removebg.png'
        with open(tempfile_path, 'rb') as input_image:
            input_data = input_image.read()
            output_data = remove(input_data)
        with open(output_path, 'wb') as output_image:
            output_image.write(output_data)
        # get the path of removedbackground image
        dist_name = os.path.basename(output_path)


    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        line_bot_api.show_loading_animation(ShowLoadingAnimationRequest(
        chat_id=userid,
        loading_seconds=10))

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                        ImageMessage(
                            original_content_url=f"{request.host_url.rstrip('/')}/static/tmp/{dist_name}",
                            preview_image_url=f"{request.host_url.rstrip('/')}/static/tmp/{dist_name}",
                            ),
                        TextMessage(text='Finish Image Task',
                                    quick_reply=QuickReply(items=get_quick_reply_items()))
                    ]
            )
        )


@handler.add(UnknownEvent)
def handle_unknown_left(event):
    app.logger.info(f"unknown event {event}")

@handler.add(MessageEvent, message=FileMessageContent)
def handle_file_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_blob_api = MessagingApiBlob(api_client)
        message_content = line_bot_blob_api.get_message_content(message_id=event.message.id)

        # save file ไปที่ /staic/tmp
        dist_path = os.path.join(static_tmp_path, event.message.file_name)
        with open(dist_path, 'wb') as f:
            f.write(message_content)

    dist_name = os.path.basename(dist_path)
    # print(dist_path)

    # Upload the file to Google Drive and get the link
    file_link = upload_to_gdrive(dist_path)
    print(file_link)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text='Upload File to Google Drive Krub.'),
                    TextMessage(text=f'{file_link[1]}',
                                quick_reply=QuickReply(items=get_quick_reply_items())),
                ]
            )
        )



if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=5000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    app.run(debug=options.debug, port=options.port)
