from firebase_admin import firestore
import threading

# from libs.configs import setConfigs
# from access import get_access_token, get_new_token

from inits import init_firebase


init_firebase()

db = firestore.client()
configs_ref = db.collection(u'redis').document(u'data')

callback_done = threading.Event()
# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
    import pdb
    pdb.set_trace()
    for doc in doc_snapshot:
        configs = doc.to_dict()
        print(configs)
        # setConfigs(configs)

configs_ref.on_snapshot(on_snapshot)

condition = threading.Condition()
condition.acquire()
condition.wait()