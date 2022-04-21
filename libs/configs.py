# from math import floor
import os
# from libs.pubsub import get_ps_2
from inits import init_firebase
from firebase_admin import firestore

init_firebase()

db = firestore.client()
# configs_ref = db.collection(u'redis').document(u'data')
configref = db.collection(u'configs').document(u'VIp4hCZGXPOqyJMNDc6H')
"""
Only for defaultable parameters
"""
CONFIGS = {
    'api_key': '7zx0e8g535qgefu6',
    'api_secret': 'utwyn9ugmbxfcx6wurcd869mtvn2ck30',
    'user_id': 'YZ7009'
}
rconfig = {}


def on_snapshot(doc_snapshot, changes, read_time):
    global rconfig
    for doc in doc_snapshot:
        rconfig = doc.to_dict()

# configref.on_snapshot(on_snapshot)


def getConfigs():
    return configref.get().to_dict()


def getConfig(varname):
    'Try to fetch data from redis first'
    # data = rconfig.get(varname, None)
    data = configref.get().to_dict()[varname]
    if(data is None):
        if(varname in CONFIGS):
            data = CONFIGS.get(varname, None)
    return data


def delConfig(varname):
    rconfig.r.hdel('configs', varname)
    # rconfig.r.save()


def setConfig(varname, val):
    # rconfig[varname] = val
    # rconfig.hsetmap('configs', {varname: val})
    configref.update({varname: val})


def setConfigs(data):
    # rconfig.hsetmap('configs', data)
    configref.update(data)
    # rconfig.r.save()


def setInitial():
    # rconfig.hsetmap('configs', CONFIGS)
    # rconfig.r.save()
    configref.update(CONFIGS)


def _getConfig(varname):
    'Try to fetch data from redis first'
    var = os.environ.get(varname)
    if(var is None):
        data = CONFIGS[varname][0]
    else:
        data = CONFIGS[varname][1](var)
    return data
