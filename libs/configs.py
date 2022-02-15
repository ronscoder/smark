from math import floor
import os
from libs.pubsub import get_ps_2

rconfig = get_ps_2()
"""
Only for defaultable parameters
"""
CONFIGS = {
    'api_key': '7zx0e8g535qgefu6',
    'api_secret': 'utwyn9ugmbxfcx6wurcd869mtvn2ck30',
    'user_id': 'YZ7009'
}


def getConfigs():
    return rconfig.hgetall('configs')


def getConfig(varname):
    'Try to fetch data from redis first'
    data = rconfig.hget('configs', varname)
    if(data is None):
        if(varname in CONFIGS):
            data = CONFIGS.get(varname, None)
    return data


def delConfig(varname):
    rconfig.r.hdel('configs', varname)
    rconfig.r.save()


def setConfig(varname, val):
    rconfig.hsetmap('configs', {varname: val})
    rconfig.r.save()


def setConfigs(data):
    rconfig.hsetmap('configs', data)
    rconfig.r.save()


def setInitial():
    rconfig.hsetmap('configs', CONFIGS)
    rconfig.r.save()


def _getConfig(varname):
    'Try to fetch data from redis first'
    var = os.environ.get(varname)
    if(var is None):
        data = CONFIGS[varname][0]
    else:
        data = CONFIGS[varname][1](var)
    return data
