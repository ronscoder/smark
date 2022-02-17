import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from libs.configs import getConfigs


# Use the application default credentials
# cred = credentials.ApplicationDefault()
cred = credentials.Certificate('smark-341423-beb738b79579.json')
firebase_admin.initialize_app(cred, {
  'projectId': 'smark-341423',
})

configs = dict(TRAIL_PC=0.05,
TRAIL_BUFFER_PC=0.02,
ENTRY_STOP_PC=0.2,
STOP_PC=0.08,
TRIGGER_GAP=1,
NIFTYBANK_QTY=25,
HOLD_EXE=False,
OPTION_PRICE_RANGE=[50, 90],
STRIKE_MID_SKIP=500,
STRIKE_LIMIT=1000,
DURATION_OPEN_POSITION_MIN=120.0,
OPEN_ORDER_EXPIRY_MIN=7,
)

db = firestore.client()
configs_ref = db.collection(u'configs').document(u'VIp4hCZGXPOqyJMNDc6H')

configs_ref.set(configs)