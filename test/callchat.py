import logging
import os
import psycopg2
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
logger = logging.getLogger(__name__)
# ID of the channel you want to send the message to
channel_id = os.environ.get("CHANNEL_ID")

# DATABASE_URL = os.environ['DATABASE_URL']

try:
        # firestore用のライブラリをインポート
    from google.cloud import firestore

    # today_countからmessage_idを取得
    db = firestore.Client(project='yoppy-chatbot')
    ref_today = db.collection('dailyreminder').document('today_count')
    docs_today = ref_today.get()
    count = docs_today.to_dict()['message_id']

    ref_message = db.collection('dailyreminder').document('messages')
    docs_message = ref_message.get()
    message = docs_message.to_dict()[f'{str(count)}']

    result = client.chat_postMessage(
        channel=channel_id,
        text=message
    )
    logger.info(result)

except SlackApiError as e:
    logger.error(f"Error posting message: {e}")
