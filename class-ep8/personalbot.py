import datetime
import errno
import os
import sys
import logging
import tempfile
from argparse import ArgumentParser

from rembg import remove

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
)

from linebot.v3.insight import (
    ApiClient as InsightClient,
    Insight
)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.INFO)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('line-channel-secret', None)
channel_access_token = os.getenv('line-access-token', None)
if channel_secret is None or channel_access_token is None:
    print('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

handler = WebhookHandler(channel_secret)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

configuration = Configuration(
    access_token=channel_access_token
)

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
        if text == 'push':
            line_bot_api.push_message(
                PushMessageRequest(
                    to=event.source.user_id,
                    messages=[TextMessage(text="Push to user")]
                )
            )
        elif text == 'emojis':
            emojis = [Emoji(index=0, product_id="5ac1bfd5040ab15980c9b435", emoji_id="001"),
                      Emoji(index=13, product_id="5ac1bfd5040ab15980c9b435", emoji_id="002")]
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='$ LINE emoji $', emojis=emojis)]
                )
            )
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=event.message.text)]
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
        
    # Output paths for rembg processing
    output_path = tempfile_path + '-removebg.png'

    # remove background then save
    with open(tempfile_path, 'rb') as input_image:
        input_data = input_image.read()
        output_data = remove(input_data)
        with open(output_path, 'wb') as output_image:
            output_image.write(output_data)
    # get the path of removedbackground image
    dist_name = os.path.basename(output_path)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                        ImageMessage(
                            original_content_url=f"{request.host_url.rstrip('/')}/static/tmp/{dist_name}",
                            preview_image_url=f"{request.host_url.rstrip('/')}/static/tmp/{dist_name}",)
                    ]
            )
        )


@handler.add(UnknownEvent)
def handle_unknown_left(event):
    app.logger.info(f"unknown event {event}")

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=5000, help='port')
    arg_parser.add_argument('-d', '--debug', default=True, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    app.run(debug=options.debug, port=options.port)