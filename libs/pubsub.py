import redis
import pickle

def get_ps_1():
    'For dynamic/runtime data'
    return PubSub(db=1)

def get_ps_2():
    'For persisting data'
    return PubSub(db=2)

def get_ps_3():
    'For meta data'
    return PubSub(db=3)

class PubSub:
    def __init__(self, db=0) -> None:
        # self.r = redis.Redis(db=db)
        self.r = redis.Redis(host='ec2-52-54-47-158.compute-1.amazonaws.com', port=29680, db=db, password='p596aaa24282fad72077b4cbfab080dc32179ba0d400919f6800c85663c06bcdf')
        self.ps = self.r.pubsub()

    def set(self, key, data):
        msg = pickle.dumps(data)
        self.r.set(key, msg)
    
    def get(self, key):
        msg = self.r.get(key)
        if(msg):
            data = pickle.loads(msg)
            return data

    def _set(self, key, msg):
        self.r.set(key, msg)
    
    def _get(self, key):
        msg = self.r.get(key)
        if(msg):
            return msg.decode('utf-8')
    
    def decode(self,data):
        return data.decode('utf-8')

    def lpush(self, key, value):
        self.r.lpush(key, pickle.dumps(value))
    
    def rpush(self, key, value):
        self.r.rpush(key, pickle.dumps(value))
    
    def lrange(self,key):
        return [pickle.loads(x) for x in self.r.lrange(key, 0, -1)]

    def hsetmap(self, name, mapping):
        self.r.hset(name, mapping={k: pickle.dumps(mapping[k]) for k in mapping})

    def hsetkv(self, name, key, value):
        self.r.hset(name, mapping={key: pickle.dumps(value)})

    def hget(self, name, key):
        data = self.r.hget(name, key)
        if(data):
            return pickle.loads(data)

    def hgetall(self, name):
        data = self.r.hgetall(name)
        if(data):
            return {k.decode('utf-8'): pickle.loads(data[k]) for k in data}
    
    def hdel(self, name, key):
        self.r.hdel(name, key)

    def hdelall(self, name):
        self.r.delete(name)

    def publish(self, channel, data):
        self.set(channel, data)
        msg = pickle.dumps(data)
        self.r.publish(channel, msg)

    def subscribe(self, channels, cb):
        self.ps.psubscribe(channels)
        for msg in self.ps.listen():
            typ = msg['type']
            if(typ=='psubscribe'):
                continue
            channel = msg['channel'].decode('utf-8')
            data = msg['data']
            dataobj = pickle.loads(data)            
            cb(channel, dataobj)
