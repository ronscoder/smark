from libs.configs import getConfigs
from plotly.subplots import make_subplots
import dash
from dash.dependencies import Input, Output, State
from dash import html
from dash import dcc
import plotly.graph_objects as go
import plotly.express as px
from libs.pubsub import get_ps_1
from direction import get_extremas

r = r3 = get_ps_1()
app = dash.Dash(__name__, title='MDashAoVs')

symbols = [['NIFTY BANK', 260105, '^NSEBANK', 'INDEX'],]
instruments = [{'symbol': x[0], 'token': x[1], 'ysymbol': x[2], 'type': x[3]}
                   for x in symbols]

configs = getConfigs()
freqfact = configs['FREQ_CUTOFF_FACTOR']
order = configs['EXTREMA_ORDER']

def getgraph(symbol):
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True)
    histohlcs = r.get(f'HISTORY_260105')
    
    divs = []
    if(not histohlcs is None):

        opens = [x['open'] for x in histohlcs]
        closes = [x['close'] for x in histohlcs]
        highs = [x['high'] for x in histohlcs]
        lows = [x['low'] for x in histohlcs]
        fig.add_trace(go.Candlestick(
            x=list(range(len(histohlcs))), open=opens, high=highs, low=lows, close=closes, name='history'), row=1, col=1)

        last_price = r.get(f'TICK_{260105}')
        fig.add_shape(type='line', x0=0, x1=len(histohlcs), y0=last_price,
                      y1=last_price, line=dict(color='blue', width=1, dash='dot'), row=1, col=1)
        bankniftysignal = r.get('BANKNIFTY_DIRECTION')
        if(not bankniftysignal is None):
            # extremas = get_extremas(closes, freqfact, order)
            extremas = bankniftysignal['extremas'] if 'extremas' in bankniftysignal else None
            direction = bankniftysignal['direction'] if 'direction' in bankniftysignal else None
            print(direction, extremas)
            if(extremas is not None):
                maximas = [(i, highs[i]) for i,x in enumerate(extremas) if x==1]
                minimas = [(i, lows[i]) for i,x in enumerate(extremas) if x==-1]
                for i,v in maximas:
                    fig.add_shape(type='line', x0=i-2, x1=i+2, y0=v,
                        y1=v, line=dict(color='red', width=2), row=1, col=1)
                for i,v in minimas:
                    fig.add_shape(type='line', x0=i-2, x1=i+2, y0=v,
                        y1=v, line=dict(color='green', width=2), row=1, col=1)
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
    dcc.Interval(id='refresher', interval=5*1000, disabled=False),
    html.Div([
        html.Div(id='contentdyn', className='p-4 flex-1 w-3/5 bg-gray-100'),
    ], className='flex flex-row w-full justify-between')
],
    className='m-4 text-sm font-mono'
)

def getPropId(ctx):
    return ctx.triggered[0]['prop_id'].split('.')[0]


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
