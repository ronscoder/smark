from libs.pubsub import get_ps_1

r = get_ps_1('kill client').r

client_id = r.client_id()
for client in r.client_list():
    # _, port = client['addr'].split(':')
    port = client['addr']
    print('killing', client['id'], client_id)
    
    if(client['id'] != client_id):
        try:
            r.client_kill(address=port)
        except:
            pass