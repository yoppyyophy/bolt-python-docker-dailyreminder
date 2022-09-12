import os
from slack_bolt import App
app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN")
)

# ここには Flask 固有の記述はありません
# App はフレームワークやランタイムに一切依存しません
@app.command("/check")
def response(ack, say, command):
    ack()

    # firestore用のライブラリをインポート
    from google.cloud import firestore

    # today_countからmessage_idを取得
    db = firestore.Client(project='yoppy-chatbot')
    ref_today = db.collection('dairyreminder').document('today_count')
    docs_today = ref_today.get()
    count = docs_today.to_dict()['message_id']

    ref_message = db.collection('dairyreminder').document('messages')
    docs_message = ref_message.get()
    message = docs_message.to_dict()[f'{str(count)}']

    say(message)

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
