from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
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
    TextMessage,
    TemplateMessage,
    ButtonsTemplate,
    MessageAction
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

# LINE Bot configuration
configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

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
    user_message = event.message.text.strip()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        print("line_bot_api: ", line_bot_api)

        if user_message in ["メニュー","こんにちは", "トイレGO"]:
            print("if文の中です")
            buttons_template = ButtonsTemplate(
                text="トイレGOを使ってみよう！\n以下の選択肢からアプリを操作してください！！",
                actions=[
                    MessageAction(label="トイレを探す", text="トイレを探す"),
                    MessageAction(label="ランキングを見る", text="ランキングを見る"),
                    MessageAction(label="最新レビューを見る", text="最新レビューを見る"),
                ]
            )
        
            template_message = TemplateMessage(
                alt_text="3つ選択肢があります",
                template=buttons_template
            )

            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )

        # 選択肢に応じた応答
        elif user_message == "トイレを探す":
            reply_text = "https://liff.line.me/2007002781-eQD6Wk94/search_toilet/"
        elif user_message == "ランキングを見る":
            reply_text = "https://liff.line.me/2007002781-eQD6Wk94/toilet_rank/"
        elif user_message == "最新レビューを見る":
            reply_text = "https://liff.line.me/2007002781-eQD6Wk94/get_latest_comment/"
        else:
            reply_text = "「メニュー」と入力し操作を選択してください!!"

        # 選択肢に応じた応答がある場合は返信
        if user_message != "メニュー" and not user_message.startswith("選択肢"):
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
