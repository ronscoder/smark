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
from direction import _calculate
import numpy as np

# r = r3 = get_ps_1('mdash')
app = dash.Dash(__name__, title='MDashAoVs')

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
        opens = [x['open'] for x in histohlcs]
        closes = [x['close'] for x in histohlcs]
        highs = [x['high'] for x in histohlcs]
        lows = [x['low'] for x in histohlcs]

        fig.add_trace(go.Candlestick(
            x=list(range(len(histohlcs))), open=opens, high=highs, low=lows, close=closes, name='history'), row=1, col=1)
        
        fig.add_vline(x=len(histohlcs_offset)-1, line=dict(color='blue', width=1, dash='dot'), row=1, col=1)

        opens = [x['open'] for x in histohlcs_offset]
        closes = [x['close'] for x in histohlcs_offset]
        highs = [x['high'] for x in histohlcs_offset]
        lows = [x['low'] for x in histohlcs_offset]

        # p_move1 = np.poly1d(np.polyfit([x for x in range(3)], closes[-5:-2], 1))
        # p_move2 = np.poly1d(np.polyfit([x for x in range(3)], closes[-3:], 1))

        # fig.add_shape(type='line', x0=len(histohlcs_offset)-5, x1=len(histohlcs_offset)-5+2, y0=p_move1(0),  y1=p_move1(2), line=dict(color='orange', width=3, dash='solid'), row=1, col=1)

        # fig.add_shape(type='line', x0=len(histohlcs_offset)-3, x1=len(histohlcs_offset)-3+2, y0=p_move2(0),  y1=p_move2(2), line=dict(color='orange', width=3, dash='solid'), row=1, col=1)

        extremas = params['extremas']
        # maximas_y = [x[1] for i,x in enumerate(extremas) if x[0] == -1][-3:-1]
        # maximas_x = [i for i,x in enumerate(extremas) if x[0] == -1][-3:-1]
        # minimas_y = [x[1] for i,x in enumerate(extremas) if x[0] == 1][-3:-1]
        # minimas_x = [i for i,x in enumerate(extremas) if x[0] == 1][-3:-1]        

        maximas_y = [x[1] for i,x in enumerate(extremas) if x[0] == -1]
        maximas_x = [i for i,x in enumerate(extremas) if x[0] == -1]
        minimas_y = [x[1] for i,x in enumerate(extremas) if x[0] == 1]
        minimas_x = [i for i,x in enumerate(extremas) if x[0] == 1]

        p_res = params['p_res']
        std = params['std']
        # print('std', std)
        if(p_res is not None):
            fig.add_shape(type='line', x0=maximas_x[0], x1=len(histohlcs_offset), y0=p_res(maximas_x[0]),  y1=p_res(len(histohlcs_offset)), line=dict(color='orange', width=3, dash='solid'), row=1, col=1)
            fig.add_shape(type='line', x0=maximas_x[0], x1=len(histohlcs_offset), y0=p_res(maximas_x[0])+std,  y1=p_res(len(histohlcs_offset))+std, line=dict(color='orange', width=3, dash='solid'), row=1, col=1)

            fig.add_shape(type='line', x0=maximas_x[0], x1=len(histohlcs_offset), y0=p_res(maximas_x[0])-std,  y1=p_res(len(histohlcs_offset))-std, line=dict(color='orange', width=3, dash='solid'), row=1, col=1)

        p_sup = params['p_sup']
        if(p_sup is not None):
            fig.add_shape(type='line', x0=minimas_x[0], x1=len(histohlcs_offset), y0=p_sup(minimas_x[0]),  y1=p_sup(len(histohlcs_offset)), line=dict(color='red', width=3, dash='solid'), row=1, col=1)
            fig.add_shape(type='line', x0=minimas_x[0], x1=len(histohlcs_offset), y0=p_sup(minimas_x[0])+std,  y1=p_sup(len(histohlcs_offset))+std, line=dict(color='red', width=3, dash='solid'), row=1, col=1)
            fig.add_shape(type='line', x0=minimas_x[0], x1=len(histohlcs_offset), y0=p_sup(minimas_x[0])-std,  y1=p_sup(len(histohlcs_offset))-std, line=dict(color='red', width=3, dash='solid'), row=1, col=1)

        if(True):
            l = len(histohlcs_offset) - 1
            if(direction ==1):
                # fig.add_shape(type='line', x0=l, x1=l, y0=max(highs)+50,
                #         y1=max(highs) - (max(highs) - min(lows))/2, line=dict(color='green', width=2, dash='solid'), row=1, col=1)
                fig.add_vline(x = l,  line=dict(color='green', width=2, dash='solid'), row=1, col=1)
            
            if(direction ==-1):
                fig.add_vline(x=l, line=dict(color='red', width=2, dash='solid'), row=1, col=1)
                
            if(extremas is not None):
                # print('extremas')
                maximas = [(i, highs[i]) for i,x in enumerate(extremas) if x[0]==-1]
                minimas = [(i, lows[i]) for i,x in enumerate(extremas) if x[0]==1]
                for i,v in maximas:
                    fig.add_shape(type='line', x0=i-1, x1=i+1, y0=v+50,
                        y1=v+50, line=dict(color='purple', width=10), row=1, col=1)
                    # fig.add_shape(type='line', x0=i-1, x1=i+1, y0=v+50,
                    #     y1=v+50, line=dict(color='purple', width=10), row=2, col=1)
                for i,v in minimas:
                    fig.add_shape(type='line', x0=i-1, x1=i+1, y0=v-50,
                        y1=v-50, line=dict(color='blue', width=10), row=1, col=1)
                    # fig.add_shape(type='line', x0=i-1, x1=i+1, y0=v-50,
                    #     y1=v-50, line=dict(color='blue', width=10), row=2, col=1)
            # if(ys is not None):
            #     fig.add_trace(go.Scatter(y=[h['close'] for h in histohlcs]), row=1, col=1)
                # fig.add_trace(go.Scatter(y=ys), row=2, col=1)
        # fig.add_trace(go.Scatter(x=[i for i,x in extremasv], y=[x for i,x in extremasv], mode="markers"))
        # for i, extrema in enumerate(extremas):
        #     if(extrema == 1):
        #         'maxima'
        #         fig.add_shape(type='circle', x0=i, x1=i, y0=last_price,
        #               y1=last_price, line=dict(color='blue', width=1, dash='dot'), row=1, col=1)

    fig.update_layout(title_text=symbol)
    # fig.update_xaxes(range=[0, 80])
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
    app.run_server(debug=True, port='8052')
