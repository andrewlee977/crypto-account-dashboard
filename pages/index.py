# Imports from 3rd party libraries
from os import getenv
from numpy import datetime_as_string
import requests
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pytz
import pandas as pd

from web3 import Web3, datastructures
from ens import ENS

# Imports from this application
from app import app

# Connect to infura endpoint
infura_url = getenv("INFURA_ENDPOINT")
w3 = Web3(Web3.HTTPProvider(infura_url))

# Connect to Etherscan API
etherscan_key = getenv('ETHERSCAN_API_KEY')

# 2 column layout. 1st column width = 4/12
# https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout
# column1 = dbc.Col(
    # [
layout = html.Div([ 
    html.Div([
        html.Br(),
        html.Br(),
        html.Br(),
        dcc.Markdown(
            """
        
            ## Track Your Crypto Assets

            View your crypto portfolio all in one place.
            Type in an address to get started 👇

            """
        ),
        dcc.Input(id='address', placeholder="Search by account address...", type="text", style={'width': '50%'}),
        html.Br(),
        html.Br(),
        dbc.Button('Search Address', id='search', n_clicks=0, style={'background-color': '#46d9e8'})
    ], style={'text-align': 'center'}),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Div(id='display_address', style={'font-size': '40px', 'color': 'white'}),
    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div(id='display_balance', style={'font-size': '40px', 'color': 'white'}),
                    html.Div(id='balance', style={'color': 'white'}),
                ])
            ], color='#636060'),
            html.Br(),
            html.Br(),
        ], width='4'),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div(id='display_ether', style={'font-size': '40px'}),
                    html.Div(id='ether_value'),
                ])
            ], color='#636060'),
            html.Br(),
            html.Br(),
        ], width='4'),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div(id='display_transaction_count', style={'font-size': '40px'}),
                    html.Div(id='transaction_count'),
                ])
            ], color='#636060'),
            html.Br(),
            html.Br(),
        ], width='4'),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='nft_graph', figure={})
                ])
            ], color='#636060'),
            html.Br(),
            html.Br(),
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='token_graph', figure={})
                ])
            ], color='#636060'),
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div(id='display_nft_transfers', style={'font-size': '40px'}),
                    html.Div(id='nft_transfers'),
                ])
            ], color='#636060'),
            html.Br(),
            html.Br(),
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div(id='display_token_transfers', style={'font-size': '40px'}),
                    html.Div(id='token_transfers'),
                ])
            ], color='#636060'),
            html.Br(),
            html.Br(),
        ])
    ])    

])

# Epoch conversion (seconds)
def epoch_conversion(epoch):
    utc_datetime = datetime.fromtimestamp(epoch)
    local_timezone = pytz.timezone('US/Pacific')
    local_datetime = utc_datetime.replace(tzinfo=pytz.utc)
    local_datetime = local_datetime.astimezone(local_timezone)
    return local_datetime

@app.callback(
    [Output(component_id='display_address', component_property='children'),
    Output(component_id='display_balance', component_property='children'),
    Output(component_id='balance', component_property='children'),
    Output(component_id='display_ether', component_property='children'),
    Output(component_id='ether_value', component_property='children'),
    Output(component_id='display_transaction_count', component_property='children'),
    Output(component_id='transaction_count', component_property='children'),
    Output(component_id='display_nft_transfers', component_property='children'),
    Output(component_id='nft_transfers', component_property='children'),
    Output(component_id='nft_graph', component_property='figure'),
    Output(component_id='display_token_transfers', component_property='children'),
    Output(component_id='token_transfers', component_property='children'),
    Output(component_id='token_graph', component_property='figure')],
    [Input(component_id='search', component_property='n_clicks')],
    [State(component_id='address', component_property='value')]
)

def get_balance(n_clicks, address):

    display_balance = "BALANCE"
    display_ether = "ETHER VALUE (USD)"
    display_transaction_count = "TRANSACTIONS"
    display_nft_transfers = "NFT TRANSFERS"
    display_token_transfers = "ERC 20 TOKENS"

    if n_clicks == 0 or address is None:
        raise PreventUpdate
    else:
        address = address.strip()
        if address[:2] == '0x':
            clean_address = Web3.toChecksumAddress(address.strip())
        else:
            ns = ENS.fromWeb3(w3)
            clean_address = ns.address(address)
        
        # find balance for address
        balance_wei = w3.eth.get_balance(clean_address)
        converted = w3.fromWei(balance_wei, 'ether') 
        balance_eth = str(converted) + ' ETH'

        # Value of Ether Balance
        response_ether = requests.get(f"https://api.etherscan.io/api?module=stats&action=ethprice&apikey={etherscan_key}")
        ether_price = response_ether.json()['result']['ethusd']
        ether_value = "$" + str(round(float(ether_price) * float(converted), 2))

        # find transaction count for address
        transaction_count = w3.eth.get_transaction_count(clean_address)

        # find how many NFT's have been transferred
        response_nft = requests.get(f"""https://api.etherscan.io/api?module=account&action=tokennfttx&address={clean_address}&startblock=0&endblock=999999999&sort=asc&apikey={etherscan_key}""")
        nft_transfers = []
        results = response_nft.json()['result']
        threshold = 50
        if len(results) <= threshold:
            for i in range(len(results)):
                if i == 0:
                    nft_transfers.append("1.) " + str(results[-1]['tokenName']) + " (" + str(results[-1]['tokenSymbol']) + ")")
                else:
                    nft_transfers.append("\n" + f", {i + 1}.) " + str(results[-1-i]['tokenName']) + " (" + str(results[-1-i]['tokenSymbol']) + ")")
        else:
            for i in range(threshold):
                if i == 0:
                    nft_transfers.append("1.) " + str(results[-1]['tokenName']) + " (" + str(results[-1]['tokenSymbol']) + ")")
                else:
                    nft_transfers.append("\n" + f", {i + 1}.) " + str(results[-1-i]['tokenName']) + " (" + str(results[-1-i]['tokenSymbol']) + ")")
        

        # VISUALIZE NFT TRANSFERS
        times = {}
        for i in range(len(results)):
            unix = int(results[i]['timeStamp'])
            time = epoch_conversion(unix)
            format_time = str(time.year) + "-" + str(time.month) + "-" + str(time.day)
            if format_time not in times:
                times[format_time] = 1
            else:
                times[format_time] += 1
        
        df = pd.DataFrame(times.items(), columns=['date', 'transfers'])
        nft_graph = px.bar(df, x='date', y='transfers', color_discrete_sequence=["white"], title="NFT TRANSFERS OVER TIME")
        nft_graph.update_layout({'xaxis_title':'TIME', 'xaxis_color': 'white', 'yaxis_color': 'white', 'yaxis_title':'TRANSFERS',
        'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)', 'title_font_color':'white', 'yaxis_showgrid':False})

        # ERC20 token transfers
        response_token = requests.get(f"""https://api.etherscan.io/api?module=account&action=tokentx&address={clean_address}&startblock=0&endblock=999999999&sort=asc&apikey={etherscan_key}""")
        token_transfers = []
        results = response_token.json()['result']
        if len(results) <= threshold:
            for i in range(len(results)):
                if i == 0:
                    token_transfers.append("1.) " + str(results[-1]['tokenName']) + " (" + str(results[-1]['tokenSymbol']) + ")")
                else:
                    token_transfers.append(f", {i + 1}.) " + str(results[-1-i]['tokenName']) + " (" + str(results[-1-i]['tokenSymbol']) + ")")
        else:
            for i in range(threshold):
                if i == 0:
                    token_transfers.append("1.) " + str(results[-1]['tokenName']) + " (" + str(results[-1]['tokenSymbol']) + ")")
                else:
                    token_transfers.append(f", {i + 1}.) " + str(results[-1-i]['tokenName']) + " (" + str(results[-1-i]['tokenSymbol']) + ")")

        # VISUALIZE ERC20 token transfers
        times = {}
        for i in range(len(results)):
            unix = int(results[i]['timeStamp'])
            time = epoch_conversion(unix)
            format_time = str(time.year) + "-" + str(time.month) + "-" + str(time.day)
            if format_time not in times:
                times[format_time] = 1
            else:
                times[format_time] += 1
        
        df = pd.DataFrame(times.items(), columns=['date', 'transfers'])
        token_graph = px.bar(df, x='date', y='transfers', color_discrete_sequence=["white"], title="ERC20 TRANSFERS OVER TIME")
        token_graph.update_layout({'xaxis_title':'TIME', 'xaxis_color': 'white', 'yaxis_color': 'white', 'yaxis_title':'TRANSFERS',
        'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)', 'title_font_color':'white', 'yaxis_showgrid':False})

    return address, display_balance, balance_eth, display_ether, ether_value, display_transaction_count, transaction_count, display_nft_transfers, nft_transfers, nft_graph, display_token_transfers, token_transfers, token_graph
