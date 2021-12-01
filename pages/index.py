# Imports from 3rd party libraries
from os import getenv
import requests
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

# Connect to infura endpoint
infura_url = getenv("INFURA_ENDPOINT")
w3 = Web3(Web3.HTTPProvider(infura_url))

# Connect to Etherscan API
etherscan_key = getenv('ETHERSCAN_API_KEY')


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
        dcc.Input(id='address', placeholder="Crypto Wallet Address", type="text", style={'width': '80%'}),
        html.Br(),
        html.Br(),
        dbc.Button('Search Address', id='search', n_clicks=0, color='primary'),

        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Div(id='display_address'),
        html.Br(),
        # html.Br(),
        dcc.Markdown("# BALANCE"),
        html.Div(id='balance'),

        html.Br(),
        html.Br(),
        dcc.Markdown("# NFT Transfers"),
        html.Div(id='nft_transfers'),


        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),


    ],
    md=4,
)

gapminder = px.data.gapminder()
# fig = px.scatter(gapminder.query("year==2007"), x="gdpPercap", y="lifeExp", size="pop", color="continent",
#            hover_name="country", log_x=True, size_max=60)

column2 = dbc.Col(
    [
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        dcc.Markdown("# TRANSACTIONS"),
        html.Div(id='transaction_count'),
        html.Br(),
        html.Br(),
        html.Br(),
        dcc.Markdown("# ERC20 Transfers"),
        html.Div(id='token_transfers'),
    ]
)

layout = dbc.Row([column1, column2])



@app.callback(
    [Output(component_id='display_address', component_property='children'),
    Output(component_id='balance', component_property='children'),
    Output(component_id='transaction_count', component_property='children'),
    Output(component_id='nft_transfers', component_property='children'),
    Output(component_id='token_transfers', component_property='children')],
    [Input(component_id='search', component_property='n_clicks')],
    [State(component_id='address', component_property='value')]
)

def get_balance(n_clicks, address):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        clean_address = Web3.toChecksumAddress(address.strip())
        print(clean_address)
        
        # find balance for address
        balance_wei = w3.eth.get_balance(clean_address)
        balance_eth = str(w3.fromWei(balance_wei, 'ether')) + ' ETH'

        # find transaction count for address
        transaction_count = w3.eth.get_transaction_count(clean_address)

        # find how many NFT's have been transferred
        response = requests.get(f"""https://api.etherscan.io/api?module=account&action=tokennfttx&address={clean_address}&startblock=0&endblock=999999999&sort=asc&apikey={etherscan_key}""")
        nft_transfers = []
        results = response.json()['result']
        for i in range(len(results)):
            if i == 0:
                nft_transfers.append(f"{i + 1}) " + str(results[i]['tokenName']) + ": " + str(results[i]['tokenSymbol']))
            else:
                nft_transfers.append(f", {i + 1}) " + str(results[i]['tokenName']) + ": " + str(results[i]['tokenSymbol']))


        # ERC20 token transfers
        response = requests.get(f"""https://api.etherscan.io/api?module=account&action=tokentx&address={clean_address}&startblock=0&endblock=999999999&sort=asc&apikey={etherscan_key}""")
        token_transfers = []
        results = response.json()['result']
        for i in range(len(results)):
            if i == 0:
                token_transfers.append(f"{i + 1}) " + str(results[i]['tokenName']) + ": " + str(results[i]['tokenSymbol']))
            else:
                token_transfers.append(f", {i + 1}) " + str(results[i]['tokenName']) + ": " + str(results[i]['tokenSymbol']))

    return address, balance_eth, transaction_count, nft_transfers, token_transfers

# @app.callback(
#     [Output(component_id='transaction_count', component_property='children')],
#     [Input(component_id=)]
# )


