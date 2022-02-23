from trailsl import action
def on_tick_handler(channel, data):
    action(channel, data)

import time
for i in range(5):
    print(f'{i}', end="\r")
    time.sleep(1)
