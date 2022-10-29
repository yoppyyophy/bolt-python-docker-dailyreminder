from google.cloud import firestore
import os

# The `project` parameter is optional and represents which project the client
# will act on behalf of. If not supplied, the client falls back to the default
# project inferred from the environment.
# db = firestore.Client(project='yoppy-chatbot')
client = firestore.Client.from_service_account_json(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))

ref = client.collection(u'dailyreminder').document('today_count')
doc = ref.get()

print(type(doc.to_dict()['message_id']))

# print(client.collection('dailyreminder').document('messages').get().to_dict())
