import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def init_firebase():
    try:
        firebase_admin.get_app()
    except:
        cred = credentials.Certificate('smark-341423-beb738b79579.json')
        firebase_admin.initialize_app(cred, {
        'projectId': 'smark-341423',
        })


if(__name__=='__main__'):
    init_firebase()