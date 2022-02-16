# Truth parameters to consider before buying or selling
from libs.pubsub import get_ps_1
p1 = get_ps_1()


def setParams():
    params = {'GENERAL': {'TIME': True}, 'BANKNIFTY': {'ON': True}}
    p1.hsetmap('PARAMS', params)

def getTruthsOf(key='GENERAL'):
    params = p1.hget('PARAMS', key=key)
    truths = [params[k] for k in params]
    return all(truths)

if(__name__ == '__main__'):
    setParams()
