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

def callchat(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """

    import logging
    import os
    # Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    # WebClient instantiates a client that can call API methods
    # When using Bolt, you can use either `app.client` or the `client` passed to listeners.
    res_bot = access_secret_version("yoppy-chatbot", "slack_bot_token", "1")    
    client = WebClient(token=res_bot.payload.data.decode("UTF-8"))
    logger = logging.getLogger(__name__)
    # ID of the channel you want to send the message to
    channel_id = os.environ.get("CHANNEL_ID")

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
