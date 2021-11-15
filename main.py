import config
from binance.enums import *
from binance.client import Client
from trade_handler import TradeHandler
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


client = Client(config.API_KEY, config.API_SECRET, tld='us')
trader = TradeHandler('BTCUSDT', 8, 1) 
current_vals = trader.setup()

app = dash.Dash(__name__)


app.layout = html.Div(children=[
    html.Title(children='Singularity'),
    html.H1(children='Singularity'),

    html.Div(id='pos', children='''
         Holding: 
    '''),

    dcc.Interval(id='timer', interval=60*1000, n_intervals=0),
    html.Div(id='ds', children='''
    ''')
])




@app.callback(Output('ds', 'children'), Output('pos', 'children'), Input('timer', 'n_intervals'))
def update_data(n):
    trader.trade()
    return f'Running for '+str(n)+' minutes', str(trader.holding)

if __name__ == '__main__':
    app.run_server(debug=True)
