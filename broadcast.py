import telegram_send
from libs.pubsub import get_ps_1


ps1 = get_ps_1()

symbol = 'NIFTY BANK'
channels = ['SIGNAL_DIRECTION_NIFTY BANK', 'TELEREPORTING', 'SMARKMSG']

def broadcaster(channel, data):
    telegram_send.send(messages=[f'<pre>{channel}: {data}</pre>'], parse_mode='html')

if __name__ == "__main__":
    print('awaiting signal', channels)
    ps1.subscribe(channels=channels, cb=broadcaster)

