import time
# from libs.pubsub import get_ps_1

# p1 = get_ps_1()
# p1.set('TEST', 'test test')
value = 0
while True:
    value += 1
    print('test#1',value)
    # print(p1.get('TEST'))
    time.sleep(5)