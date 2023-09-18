from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
import os
from slack_bolt import App
from google.cloud import firestore, secretmanager
import google_crc32c


def access_secret_version(
    project_id: str, secret_id: str, version_id: str
) -> secretmanager.AccessSecretVersionResponse:
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Verify payload checksum.
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        print("Data corruption detected.")
        return response

    return response


res_sign = access_secret_version("yoppy-chatbot", "slack_signing_secret", "1")
res_bot = access_secret_version("yoppy-chatbot", "slack_bot_token", "1")

app = App(
    # signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    signing_secret=res_sign.payload.data.decode("UTF-8"),
    token=res_bot.payload.data.decode("UTF-8")
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
def ask_item(message, say):
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
def change_to_none(ack, say):
    ack()
    count = 1
    change_count(count)
    say("今日は何も洗わない日に変更したよ！")


@app.action("pajama")
def change_to_pajama(ack, say):
    ack()
    count = 2
    change_count(count)
    say("今日はパジャマを洗う日に変更したよ！")


@app.action("towel")
def change_to_pajama(ack, say):
    ack()
    count = 3
    change_count(count)
    say("今日はタオルを洗う日に変更したよ！")


def change_count(count):
    db = firestore.Client(project='yoppy-chatbot')

    ref = db.collection('dailyreminder').document('today_count')
    ref.update({u'message_id': count})


# Flask アプリを初期化します
flask_app = Flask(__name__)

# SlackRequestHandler は WSGI のリクエストを Bolt のインターフェイスに合った形に変換します
# Bolt レスポンスからの WSGI レスポンスの作成も行います
handler = SlackRequestHandler(app)

# Flask アプリへのルートを登録します


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # handler はアプリのディスパッチメソッドを実行します
    return handler.handle(request)
