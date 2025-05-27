from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from toilet.views import home
from accounts.views import liff_login_view
import json
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

# LINE Bot configuration
# line_channel_secret = "" # gitにpushしないようにする
configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
# handler = WebhookHandler(line_channel_secret) # デプロイ前に消す


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        # get X-Line-Signature header value
        signature = request.headers.get('X-Line-Signature', '')

        # get request body as text
        body = request.body.decode('utf-8')
        request_json = json.loads(request.body.decode('utf-8'))
        # print(request_json)
        events = request_json['events']
        if not request_json["events"]:
            return HttpResponse('OK')

        # handle webhook body
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseBadRequest()

        return HttpResponse('OK')
    else:
        return HttpResponseBadRequest()


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # print("handle_message処理内: ", event)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        print("line_bot_api: ", line_bot_api)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="こんにちは")]
            )
        )

# https://liff.line.me/2007002781-eQD6Wk94/