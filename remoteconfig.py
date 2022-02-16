import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import threading
import time
from libs.configs import setConfigs


# Use the application default credentials
# cred = credentials.ApplicationDefault()
cred = credentials.Certificate('smark-341423-beb738b79579.json')
firebase_admin.initialize_app(cred, {
  'projectId': 'smark-341423',
})

db = firestore.client()
configs_ref = db.collection(u'configs').document(u'VIp4hCZGXPOqyJMNDc6H')
# Create an Event for notifying main thread.

callback_done = threading.Event()
# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
    # for doc in doc_snapshot:
    #     # configs = doc.to_dict()
    #     # print(configs)
    #     # setConfigs(configs)
    for change in changes:
        configs = change.document.to_dict()
        print(configs)
        setConfigs(configs)
    # callback_done.set()

def getRemoteConfigs():
    doc = configs_ref.get()
    configs = doc.to_dict()
    return configs

# Watch the document
configs_ref.on_snapshot(on_snapshot)

while True:
    print('remote config listening...')
    time.sleep(10)

# if(__name__=='__main__'):
#     configs = getRemoteConfigs()
#     print(configs)
#     print(configs['HOLD_EXE']==True)
    