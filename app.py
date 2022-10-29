import os
from slack_bolt import App
# firestore用のライブラリをインポート
from google.cloud import firestore

app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN")
)

# ここには Flask 固有の記述はありません
# App はフレームワークやランタイムに一切依存しません
@app.message("確認")
def response(message, say):
    # today_countからmessage_idを取得
    db = firestore.Client(project='yoppy-chatbot')
    ref_today = db.collection('dailyreminder').document('today_count')
    docs_today = ref_today.get()
    count = docs_today.to_dict()['message_id']

    ref_message = db.collection('dailyreminder').document('messages')
    docs_message = ref_message.get()
    message = docs_message.to_dict()[f'{str(count)}']

    say(message)

@app.message("変更")
def ask_item(message,say):
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "今日洗うものを選んでね！"
                }
            },
            {
                "type": "divider"
            },
            {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "今日はお休み",
                    },
                    "action_id": "none"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "パジャマ"
                    },
                    "action_id": "pajama"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "タオル"
                    },
                    "action_id": "towel"
                }
            ]
        }
    ]
    say(
        blocks=blocks
    )

@app.action("none")
def change_to_none(ack,say):
    ack()
    count = 1
    change_count(count)
    say("今日は何も洗わない日に変更したよ！")

@app.action("pajama")
def change_to_pajama(ack,say):
    ack()
    count = 2
    change_count(count)
    say("今日はパジャマを洗う日に変更したよ！")

@app.action("towel")
def change_to_pajama(ack,say):
    ack()
    count = 3
    change_count(count)
    say("今日はタオルを洗う日に変更したよ！")

def change_count(count):
    db = firestore.Client(project='yoppy-chatbot')

    ref = db.collection('dailyreminder').document('today_count')
    ref.update({u'message_id': count})

# Flask アプリを初期化します
from flask import Flask, request
flask_app = Flask(__name__)

# SlackRequestHandler は WSGI のリクエストを Bolt のインターフェイスに合った形に変換します
# Bolt レスポンスからの WSGI レスポンスの作成も行います
from slack_bolt.adapter.flask import SlackRequestHandler
handler = SlackRequestHandler(app)

# Flask アプリへのルートを登録します
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # handler はアプリのディスパッチメソッドを実行します
    return handler.handle(request)
