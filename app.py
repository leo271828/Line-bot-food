import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message, send_image_url

load_dotenv()


machine = TocMachine(
    states=["user", "menu", "view", "food", "cost", "place", "commend", 
            "view_list", "view_new", "view_link", "view_done"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "view",
            "conditions": "is_going_to_view",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "food",
            "conditions": "is_going_to_food",
        },
        {
            "trigger": "advance",
            "source": "food",
            "dest": "cost",
            "conditions": "is_going_to_cost",
        },
        {
            "trigger": "advance",
            "source": "cost",
            "dest": "place",
            "conditions": "is_going_to_place",
        },
        {
            "trigger": "advance",
            "source": "place",
            "dest": "commend",
            "conditions": "is_going_to_commend",
        },
        {
            "trigger": "advance",
            "source": "view",
            "dest": "view_list",
            "conditions": "is_going_to_view_list",
        },
        {
            "trigger": "advance",
            "source": "view",
            "dest": "view_new",
            "conditions": "is_going_to_view_new",
        },
        {
            "trigger": "advance",
            "source": "view_new",
            "dest": "food",
            "conditions": "is_going_to_food",
        },
        {
            "trigger": "advance",
            "source": "place",
            "dest": "view_link",
            "conditions": "is_going_to_view_link",
        },
        {
            "trigger": "advance",
            "source": "view_link",
            "dest": "view_done",
            "conditions": "is_going_to_view_done",
        },
        {"trigger": "go_back", "source": ["menu", "view", "food", "cost", "place", "commend", "view_list", "view_new", "view_link", "view_done"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        # print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            if event.message.text.lower() == 'fsm':
                path = "https://bb09-111-255-52-130.jp.ngrok.io/show-fsm"
                send_image_url(event.reply_token, path)
            elif event.message.text.lower() == 'back' and machine.state != 'user' :
                send_text_message(event.reply_token, '貝殼!')
                machine.go_back()
            else:
                if machine.state != 'user':
                    send_text_message(event.reply_token, "如果要回到最一開始的狀態，請輸入「back」！")
                else:
                    send_text_message(event.reply_token, "輸入「menu」就可以開始囉！")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
