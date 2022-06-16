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
from direction import _calculate, get_training_data, boundary_overshoot
import numpy as np

# r = r3 = get_ps_1('mdash')
app = dash.Dash(__name__, title='MDashAoVs')

symbols = [['NIFTY BANK', 260105, '^NSEBANK', 'INDEX'],]
instruments = [{'symbol': x[0], 'token': x[1], 'ysymbol': x[2], 'type': x[3]}
                   for x in symbols]
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
        direction, params = boundary_overshoot(histohlcs_offset)
        print('direction', direction, params)
        opens = [x['open'] for x in histohlcs]
        closes = [x['close'] for x in histohlcs]
        highs = [x['high'] for x in histohlcs]
        lows = [x['low'] for x in histohlcs]
        # labels = [x['timestamp'] for x in histohlcs]
        # print(histohlcs[-1])
        # print(labels)
        fig.add_trace(go.Candlestick(
            x=list(range(len(histohlcs))), open=opens, high=highs, low=lows, close=closes, name='history'), row=1, col=1)

        fig.add_vline(x=len(histohlcs_offset)-1, line=dict(color='blue', width=1, dash='dot'), row=1, col=1)

        top = params['top']
        bottom = params['bottom']
        boundary_window_size = params['boundary_window_size']
        boundary_pc = params['boundary_pc']
        cboundary_pc = ((top - bottom)/bottom)*100
        mtop = (top*(1+(boundary_pc/100)/2))
        mbot = (bottom*(1-(boundary_pc/100)/2))
        
        fig.add_shape(type='line', x0=len(histohlcs_offset)-2*boundary_window_size, x1=len(histohlcs_offset)+2*boundary_window_size, y0=top,  y1=top, line=dict(color='orange', width=2, dash='solid'), row=1, col=1)

        fig.add_shape(type='line', x0=len(histohlcs_offset)-2*boundary_window_size, x1=len(histohlcs_offset)+2*boundary_window_size, y0=bottom,  y1=bottom, line=dict(color='green', width=2, dash='solid'), row=1, col=1)

        fig.add_shape(type='line', x0=len(histohlcs_offset)-2*boundary_window_size, x1=len(histohlcs_offset)+2*boundary_window_size, y0=mtop,  y1=mtop, line=dict(color='orange', width=2, dash='dot'), row=1, col=1)

        fig.add_shape(type='line', x0=len(histohlcs_offset)-2*boundary_window_size, x1=len(histohlcs_offset)+2*boundary_window_size, y0=mbot,  y1=mbot, line=dict(color='green', width=2, dash='dot'), row=1, col=1)

        fig.add_shape(type='line', x0=len(histohlcs_offset)-boundary_window_size-2, x1=len(histohlcs_offset)-boundary_window_size-2, y0=top+100,  y1=bottom-100, line=dict(color='green', width=1, dash='solid'), row=1, col=1)

        fig.add_shape(type='line', x0=len(histohlcs_offset)-2, x1=len(histohlcs_offset)-2, y0=top+100,  y1=bottom-100, line=dict(color='green', width=1, dash='solid'), row=1, col=1)
        
        if(True):
            l = len(histohlcs_offset) - 1
            if(direction ==1):
                fig.add_vline(x = l,  line=dict(color='green', width=2, dash='solid'), row=1, col=1)
            if(direction ==-1):
                fig.add_vline(x=l, line=dict(color='red', width=2, dash='solid'), row=1, col=1)
                

    fig.update_layout(title_text=symbol)
    # fig.update_xaxes(
    #     rangeslider_visible=True,
    #     rangebreaks=[
    #         # NOTE: Below values are bound (not single values), ie. hide x to y
    #         dict(bounds=["sat", "mon"]),  # hide weekends, eg. hide sat to before mon
    #         dict(bounds=[15.5, 9.5], pattern="hour"),  # hide hours outside of 9.30am-4pm
    #         # dict(values=["2020-12-25", "2021-01-01"])  # hide holidays (Christmas and New Year's, etc)
    #     ]
    # )
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
