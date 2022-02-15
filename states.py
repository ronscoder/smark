from libs.configs import getConfigs, setConfigs
from libs.pubsub import get_ps_1

p1 = get_ps_1()

while True:
    print()
    print('-'*30)
    print('CONFIGS')
    confs = getConfigs()
    for k in confs:
        print(k, confs[k])

    print()
    print('CURRENT_BUY_ORDER')
    print(p1.get('CURRENT_BUY_ORDER'))

    print()
    print('-'*30)
    cmd = '''
    C = Clear order
    Other keys to continue
    '''
    value = input(cmd)
    if(value == 'C'):
        p1.r.delete('CURRENT_BUY_ORDER')