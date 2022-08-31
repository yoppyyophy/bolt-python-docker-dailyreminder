import os
import psycopg2
from unittest import case
from slack_bolt import App
app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN")
)

DATABASE_URL = os.environ['DATABASE_URL']

# ここには Flask 固有の記述はありません
# App はフレームワークやランタイムに一切依存しません
@app.command("/check")
def response(ack, say, command):
    ack()
    with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT message_text FROM messages WHERE message_id = (SELECT message_id FROM today_count)')
            data = cur.fetchall()

    message_text = data[0][0]
    say(message_text)

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
