from libs.pubsub import get_ps_1


import pickle

# file = f'sample/HISTORY_260105_{input("suffix: ")}'
ps1 = get_ps_1('test_history')

import os

while(True):
    history = ps1.get('HISTORY_260105')
    if(not history is None):
        # print('length', len(history))
        # offset = int(input('upto: '))
        # data = history[:offset+1]
        data = history
        with open('sample/history', 'wb') as f:
            pickle.dump(history, f)
        with open('sample/history_offset', 'wb') as f:
            pickle.dump(data, f)
    if(input('continue?')!=''):
        break
# history = None
# if(os.path.exists(file)):
#     with open(file, 'rb') as f:
#         history = pickle.load(f)
# else:
#     ps1 = get_ps_1('test_history')
#     history = ps1.get('HISTORY_260105')
#     with open(file, 'wb') as f:
#         pickle.dump(history, f)

# while(True):
#     if(not history is None):
#         print('length', len(history))
#         offset = int(input('upto: '))
#         data = history[:offset+1]
#         with open('sample/history', 'wb') as f:
#             pickle.dump(history, f)
#         with open('sample/history_offset', 'wb') as f:
#             pickle.dump(data, f)