# import firebase_admin
# from firebase_admin import credentials
from firebase_admin import firestore

import threading

# from libs.configs import setConfigs
from access import get_access_token, get_new_token

# Use the application default credentials
# cred = credentials.ApplicationDefault()
# cred = credentials.Certificate('smark-341423-beb738b79579.json')
# firebase_admin.initialize_app(cred, {
#   'projectId': 'smark-341423',
# })
from inits import init_firebase

init_firebase()

db = firestore.client()
# configs_ref = db.collection(u'configs').document(u'VIp4hCZGXPOqyJMNDc6H')
access_ref = db.collection(u'configs').document(u'access')
# Create an Event for notifying main thread.

callback_done = threading.Event()
# Create a callback on_snapshot function to capture changes
# def on_snapshot(doc_snapshot, changes, read_time):
#     for doc in doc_snapshot:
#         configs = doc.to_dict()
#         print(configs)
#         setConfigs(configs)

def on_access_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        configs = doc.to_dict()
        if('request_token' in configs):
            access_token = get_access_token()
            if(access_token is None):
                # import pdb
                # pdb.set_trace()
                get_new_token(configs['request_token'])

# def getRemoteConfigs():
#     doc = configs_ref.get()
#     configs = doc.to_dict()
#     return configs

# Watch the document
# configs_ref.on_snapshot(on_snapshot)
access_ref.on_snapshot(on_access_snapshot)

condition = threading.Condition()
condition.acquire()
condition.wait()