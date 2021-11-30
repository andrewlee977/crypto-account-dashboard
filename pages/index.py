# Imports from 3rd party libraries
from os import getenv
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px

from web3 import Web3

# Imports from this application
from app import app

infura_url = getenv("INFURA_ENDPOINT")
web3 = Web3(Web3.HTTPProvider(infura_url))



# 2 column layout. 1st column width = 4/12
# https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout
column1 = dbc.Col(
    [
        dcc.Markdown(
            """
        
            ## Track Your Crypto Assets

            View your crypto portfolio all in one place. 

            """
        ),
        dcc.Input(id='address', placeholder="Ethereum Wallet Address", type="text", style={'width': '80%'}),
        html.Br(),
        html.Br(),
        dbc.Button('Search Address', id='search', n_clicks=0, color='primary'),


        html.Br(),
        html.Br(),
        dcc.Markdown("# BALANCE"),
        html.Div(id='balance'),
    ],
    md=4,
)

gapminder = px.data.gapminder()
# fig = px.scatter(gapminder.query("year==2007"), x="gdpPercap", y="lifeExp", size="pop", color="continent",
#            hover_name="country", log_x=True, size_max=60)

column2 = dbc.Col(
    [
        # dcc.Graph(figure=fig),
        # html.Img(src="assets/crypto-dashboard.jpeg", width='725px', height='400px')
    ]
)

layout = dbc.Row([column1, column2])



@app.callback(
    Output(component_id='balance', component_property='children'),
    [Input(component_id='search', component_property='n_clicks'),
    Input(component_id='address', component_property='value')]
)

def get_balance(n_clicks, address):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        balance_wei = web3.eth.getBalance(address)
        balance_eth = web3.fromWei(balance_wei, 'ether')
        n_clicks = 0

    return str(balance_eth) + ' ETH'


