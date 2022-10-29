from google.cloud import firestore

db = firestore.Client(project='yoppy-chatbot')

ref = db.collection('dailyreminder').document('today_count')
docs = ref.get()

count = docs.to_dict()['message_id']

count += 1
if count > 3:
    count = 1

ref.update({u'message_id': count})
