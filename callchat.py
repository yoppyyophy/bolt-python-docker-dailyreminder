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

DATABASE_URL = os.environ['DATABASE_URL']

try:
    # Call the chat.postMessage method using the WebClient
    with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT message_text FROM messages WHERE message_id = (SELECT message_id FROM today_count)')
            data = cur.fetchall()

    message_text = data[0][0]
    result = client.chat_postMessage(
        channel=channel_id,
        text=message_text
    )
    logger.info(result)

except SlackApiError as e:
    logger.error(f"Error posting message: {e}")
