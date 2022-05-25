# from libs.configs import getConfigs
from plotly.subplots import make_subplots
import dash
from dash.dependencies import Input, Output, State
from dash import html
from dash import dcc
import plotly.graph_objects as go
import plotly.express as px
# from libs.pubsub import get_ps_1
# from direction import get_extremas
import pickle
import os
from direction import _calculate, get_training_data, get_extremas
from libs.calcs import get_extremas
import numpy as np

# r = r3 = get_ps_1('mdash')
app = dash.Dash(__name__, title='MDash3AoVs')

symbols = [['NIFTY BANK', 260105, '^NSEBANK', 'INDEX'],]
instruments = [{'symbol': x[0], 'token': x[1], 'ysymbol': x[2], 'type': x[3]}
                   for x in symbols]

# configs = getConfigs()
# freqfact = configs['FREQ_CUTOFF_FACTOR']
# order = configs['EXTREMA_ORDER']

def getgraph(symbol):
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True)
    histohlcs = None
    fpath = 'sample/history'
    if(os.path.exists(fpath)):
        with open(fpath, 'rb') as f:
            histohlcs = pickle.load(f)

    fpathoffset = 'sample/history_offset'
    histohlcs_offset=None
    if(os.path.exists(fpathoffset)):
        with open(fpathoffset, 'rb') as f:
            histohlcs_offset = pickle.load(f)
    
    divs = []
    if(not (None in (histohlcs, histohlcs_offset))):
        direction, params = _calculate(histohlcs_offset)
        # print('direction', direction, 'std', params['std'])
        opens = [x['open'] for x in histohlcs]
        closes = [x['close'] for x in histohlcs]
        highs = [x['high'] for x in histohlcs]
        lows = [x['low'] for x in histohlcs]
        labels = [x['timestamp'] for x in histohlcs]
        # extremas, _ = get_extremas(closes, )
        print(histohlcs[-1])
        # fig.add_trace(go.Candlestick(
        #     x=list(range(len(histohlcs))), open=opens, high=highs, low=lows, close=closes, name='history'), row=1, col=1)
        fig.add_trace(go.Candlestick(
            x=labels, open=opens, high=highs, low=lows, close=closes, name='history'), row=1, col=1)
        # fig.add_trace(go.Candlestick(
        #     x=[v['timestamp'] for v in histohlcs], open=opens, high=highs, low=lows, close=closes, name='history'), row=1, col=1)
        
        fig.add_vline(x=labels[len(histohlcs_offset)-1], line=dict(color='blue', width=1, dash='dot'), row=1, col=1)

        opens = [x['open'] for x in histohlcs_offset]
        closes = [x['close'] for x in histohlcs_offset]
        ltp = closes[-1]
        highs = [x['high'] for x in histohlcs_offset]
        lows = [x['low'] for x in histohlcs_offset]

        extremas = params['extremas']
        
        if(True):
            l = len(histohlcs_offset) - 1
            # if(direction ==1):
            #     fig.add_vline(x = labels[l],  line=dict(color='green', width=2, dash='solid'), row=1, col=1)
            
            # if(direction ==-1):
            #     fig.add_vline(x=labels[l], line=dict(color='red', width=2, dash='solid'), row=1, col=1)
                
            if(extremas is not None):
                maximas = [(i, highs[i]) for i,x in enumerate(extremas) if x[0]==-1]
                minimas = [(i, lows[i]) for i,x in enumerate(extremas) if x[0]==1]
                levels = [*maximas, *minimas]
                upforce = sum([1-1/((v-ltp)**2) for i,v in levels if v > ltp])
                downforce = sum([1-1/((ltp-v)**2) for i,v in levels if v < ltp])
                up = upforce/(upforce+downforce)
                down = downforce/(upforce+downforce)
                print('up', up, 'down', down)
                # fig.add_annotation(x=len(histohlcs_offset)-1, y=max(highs),text=f"up:{round(up,1)} down:{round(down,1)}", showarrow=True,arrowhead=1)
                for i,v in maximas:
                    fig.add_shape(type='line', x0=labels[i], x1=labels[-1], y0=v,
                        y1=v, line=dict(color='purple', width=1, dash='dot'), row=1, col=1)
                for i,v in minimas:
                    fig.add_shape(type='line', x0=labels[i], x1=labels[-1], y0=v,
                        y1=v, line=dict(color='green', width=1, dash='solid'), row=1, col=1)
    fig.update_layout(title_text=symbol)
    # fig.update_xaxes(xaxis=dict(type = "category"))
    fig.update_xaxes(
        rangeslider_visible=True,
        rangebreaks=[
            # NOTE: Below values are bound (not single values), ie. hide x to y
            dict(bounds=["sat", "mon"]),  # hide weekends, eg. hide sat to before mon
            dict(bounds=[15.5, 9.5], pattern="hour"),  # hide hours outside of 9.30am-4pm
            # dict(values=["2020-12-25", "2021-01-01"])  # hide holidays (Christmas and New Year's, etc)
        ]
    )
    return html.Div([dcc.Graph(id='graph1', figure=fig),
                     *divs
                     ])

app.layout = html.Div(children=[
    html.Div('HISTORY_260105', id='txt-symbol', hidden=True),
    html.Button('PAUSE', id='btn_pause'),
    dcc.Interval(id='refresher', interval=5*1000, disabled=False),
    html.Div([
        html.Div(id='contentdyn', className='p-4 flex-1 w-3/5 bg-gray-100'),
    ], className='flex flex-row w-full justify-between')
],
    className='m-4 text-sm font-mono'
)

def getPropId(ctx):
    return ctx.triggered[0]['prop_id'].split('.')[0]

# @ app.callback(Output('btn_pause', 'children'), Input('btn_pause', 'n_clicks'))
# def pause(n_clicks):
#     # paused = r.get('PAUSED')
#     print(paused, n_clicks)
#     if(paused is None):
#         paused = False
#     if(n_clicks is None):
#         pass
#     else:
#         # r.set('PAUSED', not paused)
#     return 'paused' if paused else 'pause'


@ app.callback(Output('contentdyn', 'children'),
               Input(component_id='refresher',
                     component_property='n_intervals'),
               Input('txt-symbol', 'children')
               )
def updateContent(ninterval, symbol):
    fig = getgraph(symbol)
    # last_price = r.get(f'last_price-{symbol}')
    return [
        fig,
        html.Div([], className='flex flex-row'),
    ]

if(__name__ == '__main__'):
    print('running...')
    # app.
    # run_server(app)
    app.run_server(debug=True, port='8053')
