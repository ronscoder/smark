import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from bs4 import BeautifulSoup
import requests

def init_firebase():
    try:
        firebase_admin.get_app()
    except:
        cred = credentials.Certificate('smark-341423-beb738b79579.json')
        firebase_admin.initialize_app(cred, {
        'projectId': 'smark-341423',
        })

def get_nums_after(stext, text):
    nums = []
    idx = text.find(stext)
    if(idx==-1):
        return nums
    subtexts = text[idx+len(stext):].split(' ')
    for subtext in subtexts:
        try:
            num = int(subtext)
            nums.append(num)
        except:
            pass
    return nums
        

def update_nifty_contracts_allowed():
    bs = BeautifulSoup(requests.get('https://zerodha.com/margin-calculator/SPAN/').text, 'html.parser')
    text = bs.find(lambda tag: 'Bank Nifty contracts allowed for trading' in tag.text and tag.name=='label').parent.find('strong').contents
    
    text_current_week = text[0]
    current_week_strikes = get_nums_after('MIS:', text_current_week)
    update_vals = {}
    update_vals['STRIKES.CURRENT_WEEK.ALL'] = True if len(current_week_strikes)==0 else False
    if(len(current_week_strikes)>0):
        update_vals['STRIKES.CURRENT_WEEK.LOW'] = min(current_week_strikes)
        update_vals['STRIKES.CURRENT_WEEK.HIGH'] = max(current_week_strikes)

    text_next_week = text[2]
    next_week_strikes = get_nums_after('MIS:', text_next_week)
    update_vals['STRIKES.NEXT_WEEK.ALL'] = True if len(next_week_strikes)==0 else False
    if(len(next_week_strikes)>0):
        update_vals['STRIKES.NEXT_WEEK.LOW'] = min(next_week_strikes)
        update_vals['STRIKES.NEXT_WEEK.HIGH'] = max(next_week_strikes)

    text_next_month = text[4]
    next_month_strikes = get_nums_after('MIS:', text_next_month)
    update_vals['STRIKES.NEXT_MONTH.ALL'] = True if len(next_month_strikes)==0 else False
    if(len(next_month_strikes)>0):
        update_vals['STRIKES.NEXT_MONTH.LOW'] = min(next_month_strikes)
        update_vals['STRIKES.NEXT_MONTH.HIGH'] = max(next_month_strikes)
    print(update_vals)
    # return
    db = firestore.client()
    db.collection(u'configs').document(u'VIp4hCZGXPOqyJMNDc6H').update(update_vals)


if(__name__=='__main__'):
    init_firebase()
    update_nifty_contracts_allowed()