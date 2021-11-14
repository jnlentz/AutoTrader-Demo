import config
from binance.enums import *
from binance.client import Client
from trade_handler import TradeHandler
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import views as vt


client = Client(config.API_KEY, config.API_SECRET, tld='us')
trader = TradeHandler('LTCUSDT', 5) 
current_vals = trader.setup()

app = dash.Dash(__name__)

# Candlestick chart
kline_chart = vt.kline_chart(trader.df, trader.asset.symbol)
# RSI chart
rsi_chart = vt.rsi_chart(trader.df)

app.layout = html.Div(children=[
    html.Title(children='Singularity'),
    html.H1(children='Singularity'),

    html.Div(id='pos', children='''
         Current Position: 
    '''),

    dcc.Graph(id='kline_chart', figure=kline_chart), 

    dcc.Graph(id='rsi_chart', figure=rsi_chart),

    dcc.Interval(id='timer', interval=60*1000, n_intervals=0),
    html.Div(id='ds', children='''
    ''')
])

app.layout = html.Div(children = [    
                html.Div(className='row', children=[            
                    html.Div(className='four columns div-user-controls', children=[                    
                        html.H2('AutoTrader'),
                        html.Div(["Trading pair: ",
                            dcc.Input(id="symbol", type="text", placeholder="", style={'marginRight':'10px'})]),
                        html.Button(id='submit-button', n_clicks=0, children='Fetch')
                        ]),
                html.Div(className='eight columns div-for-charts bg-grey',
                    children=[
                        dcc.Graph(id='kline_chart', figure=kline_chart), 
                        dcc.Graph(id='rsi_chart', figure=rsi_chart),
                    ])
                ])
            ])


@app.callback(Output('ds', 'children'), Input('timer', 'n_intervals'))
def update_data(n):
    #trader.spin()
    return f'Running for '+str(n)+' minutes'
    
@app.callback(Output('pos', 'children'), Input('timer', 'n_intervals'))
def update_data(n):
    return f'Current position: ' + str(trader.position)

@app.callback(Output('kline_chart', 'figure'), Input('timer', 'n_intervals'))
def update_klines(n):
    kline_chart = vt.kline_chart(trader.df, trader.pair.symbol)
    return kline_chart

@app.callback(Output('rsi_chart', 'figure'), Input('timer', 'n_intervals'))
def update_rsi(n):
    rsi_chart = vt.rsi_chart(trader.df)
    return rsi_chart    

if __name__ == '__main__':
    app.run_server(debug=True)
