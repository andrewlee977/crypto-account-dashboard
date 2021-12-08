# Imports from 3rd party libraries
from os import getenv
# from numpy import datetime_as_string
import requests
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
# import dash_core_components as dcc
# import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pytz
import pandas as pd

from web3 import Web3
from ens import ENS

# Imports from this application
from app import app

# Connect to infura endpoint
infura_url = getenv("INFURA_ENDPOINT")
w3 = Web3(Web3.HTTPProvider(infura_url))

# Connect to Etherscan API
etherscan_key = getenv('ETHERSCAN_API_KEY')


layout = html.Div([ 
    html.Div([
        html.Br(),
        html.Br(),
        html.Br(),
        dcc.Markdown(
            """
            ## Track Your Ethereum Assets
            """
        ),
        dcc.Input(id='address', placeholder="Search by account or ENS name...", type="text", style={'width': '50%'}),
        html.Br(),
        html.Br(),
        dbc.Button('Search', id='search', n_clicks=0, style={'background-color': '#46d9e8'})
    ], style={'text-align': 'center'}),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),

    dbc.Card([
        dbc.CardBody([
            html.Div(id='display_address', style={'font-size': '20px', 'color': 'white'}),
            html.Br(),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id='display_balance', style={'font-size': '20px', 'color': 'white'}),
                            html.Div(id='balance', style={'color': 'white'}),
                        ])
                    ], color='#303030'),
                    html.Br(),
                    html.Br(),
                ], width='4'),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id='display_ether', style={'font-size': '20px'}),
                            html.Div(id='ether_value'),
                        ])
                    ], color='#303030'),
                    html.Br(),
                    html.Br(),
                ], width='4'),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id='display_transaction_count', style={'font-size': '20px'}),
                            html.Div(id='transaction_count'),
                        ])
                    ], color='#303030'),
                    html.Br(),
                    html.Br(),
                ], width='4'),
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id='display_nft_graph', style={'font-size': '20px'}),
                            dcc.Graph(id='nft_graph', figure={})
                        ])
                    ], color='#303030'),
                    html.Br(),
                    html.Br(),
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id='display_token_graph', style={'font-size': '20px'}),
                            dcc.Graph(id='token_graph', figure={})
                        ])
                    ], color='#303030'),
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id='display_nft_transfers', style={'font-size': '20px'}),
                            html.Div(id='nft_transfers'),
                        ])
                    ], color='#303030'),
                    html.Br(),
                    html.Br(),
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id='display_token_transfers', style={'font-size': '20px'}),
                            html.Div(id='token_transfers'),
                        ])
                    ], color='#303030'),
                    html.Br(),
                    html.Br(),
                ])
            ]),
            
            # dbc.Row([
            #     dbc.Col([
            #         dbc.Card([
            #             dbc.CardBody([
            #                 # html.Div(id='nft_worth_in_usd')
            #             ])
            #         ])
            #     ]),
            #     dbc.Col([
            #         dbc.Card([
            #             dbc.CardBody([
            #                 html.Br(),
            #             ])
            #         ])
            #     ])
            # ]),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(id="loading-1", children=[html.Div(id='display_nft_holdings', style={'font-size': '20px'})],type='circle'),
                            html.Div(id='nft_worth_in_usd'),
                            html.Div(id='nft_images')
                        ])
                    ], color='#303030')
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(id='loading-2', children=[html.Div(id='display_token_holdings', style={'font-size': '20px'})],type='circle'),
                            html.Div(id='token_images')
                        ])
                    ], color='#303030')
                ], width=6)
            ])
        ])
    ], color='#222222', style={"border": "thin solid #303030"})    
])


# Epoch conversion (seconds)
def epoch_conversion(epoch):
    """Converts unix time to datetime object"""
    utc_datetime = datetime.fromtimestamp(epoch)
    local_timezone = pytz.timezone('US/Pacific')
    local_datetime = utc_datetime.replace(tzinfo=pytz.utc)
    local_datetime = local_datetime.astimezone(local_timezone)
    return local_datetime


def address_to_checksum(address):
    """Converts Ethereum address (0x or ENS) to Checksum address"""
    address = address.strip()
    if address[:2] == '0x':
        clean_address = Web3.toChecksumAddress(address)
    else:
        # Converts ENS address to checksum address
        ns = ENS.fromWeb3(w3)
        clean_address = ns.address(address)
    return clean_address


def address_to_ens(checksum_address):
    """
    Converts Checksum address to ENS name associated with that account
    """
    ns = ENS.fromWeb3(w3)
    clean_address = ns.name(checksum_address)
    return clean_address


def wei_to_ether(balance_wei):
    """Takes in Wei value (int) and returns Eth balance (float)"""
    balance_eth = float(w3.fromWei(balance_wei, 'ether'))
    return balance_eth

def ether_in_usd(ether_value):
    response_ether = requests.get(f"https://api.etherscan.io/api?module=stats&action=ethprice&apikey={etherscan_key}")
    ether_price = response_ether.json()['result']['ethusd']
    ether_usd = "$" + str(round(float(ether_price) * float(ether_value), 2))
    return ether_usd


@app.callback(
    [Output(component_id='display_address', component_property='children'),
    Output(component_id='display_balance', component_property='children'),
    Output(component_id='balance', component_property='children'),
    Output(component_id='display_ether', component_property='children'),
    Output(component_id='ether_value', component_property='children'),
    Output(component_id='display_transaction_count', component_property='children'),
    Output(component_id='transaction_count', component_property='children')],
    [Input(component_id='search', component_property='n_clicks')],
    [State(component_id='address', component_property='value')]
)

def get_balance(n_clicks, address):
    """
    Function takes in n_clicks and Ethereum address and outputs
    the address's Address, Balance, Ether Value, and # of Transactions
    """

    if n_clicks == 0 or address is None:
        raise PreventUpdate
    else:
        # App section titles
        display_balance = "BALANCE"
        display_ether = "ETHER VALUE (USD)"
        display_transaction_count = "TRANSACTIONS"

        # Cleans and converts address to Checksum Address
        clean_address = address_to_checksum(address)

        # Get address name (ENS)
        ens_address = address_to_ens(clean_address)

        # Find ETH balance for address
        balance_wei = w3.eth.get_balance(clean_address)
        converted = wei_to_ether(balance_wei)
        balance_eth = str(converted) + ' ETH'

        # Value of Ether Balance in USD
        ether_value = ether_in_usd(converted)

        # Find transaction count for address
        transaction_count = w3.eth.get_transaction_count(clean_address)

    return ens_address, display_balance, balance_eth, display_ether, ether_value, display_transaction_count, transaction_count



@app.callback(
    [Output(component_id='display_nft_transfers', component_property='children'),
    Output(component_id='nft_transfers', component_property='children'),
    Output(component_id='display_nft_graph', component_property='children'),
    Output(component_id='nft_graph', component_property='figure'),
    Output(component_id='display_token_transfers', component_property='children'),
    Output(component_id='token_transfers', component_property='children'),
    Output(component_id='display_token_graph', component_property='children'),
    Output(component_id='token_graph', component_property='figure')],
    [Input(component_id='search', component_property='n_clicks')],
    [State(component_id='address', component_property='value')]
)

def nft_token_display(n_clicks, address):
    """
    Function takes in n_clicks and Ethereum address and outputs
    the address's NFT transfers over time graph, ERC20 transfers 
    over time graph, Recent NFT transfers, and Recent ERC20 Token transfers
    """
    if n_clicks == 0 or address is None:
        raise PreventUpdate
    else:
        # App section titles
        display_nft_transfers = "RECENT NFT TRANSFERS"
        display_token_transfers = "RECENT ERC20 TOKENS"
        display_nft_graph = "NFT TRANSFERS OVER TIME"
        display_token_graph = "ERC20 TRANSFERS OVER TIME"

        # Cleans and converts address to Checksum Address
        clean_address = address_to_checksum(address)

        # find how many NFT's have been transferred
        response_nft = requests.get(f"""https://api.etherscan.io/api?module=account&action=tokennfttx&address={clean_address}&startblock=0&endblock=999999999&sort=asc&apikey={etherscan_key}""")
        nft_transfers = []
        results_nft = response_nft.json()['result']
        threshold = 25
        if len(results_nft) <= threshold:
            for i in range(len(results_nft)):
                if i == 0:
                    nft_transfers.append("1.) " + str(results_nft[-1]['tokenName']) + " (" + str(results_nft[-1]['tokenSymbol']) + ")")
                else:
                    nft_transfers.append(f", {i + 1}.) " + str(results_nft[-1-i]['tokenName']) + " (" + str(results_nft[-1-i]['tokenSymbol']) + ")")
        else:
            for i in range(threshold):
                if i == 0:
                    nft_transfers.append("1.) " + str(results_nft[-1]['tokenName']) + " (" + str(results_nft[-1]['tokenSymbol']) + ")")
                else:
                    nft_transfers.append(f", {i + 1}.) " + str(results_nft[-1-i]['tokenName']) + " (" + str(results_nft[-1-i]['tokenSymbol']) + ")")
        

        # VISUALIZE NFT TRANSFERS
        times = {}
        for i in range(len(results_nft)):
            unix = int(results_nft[i]['timeStamp'])
            time = epoch_conversion(unix)
            format_time = str(time.year) + "-" + str(time.month) + "-" + str(time.day)
            if format_time not in times:
                times[format_time] = 1
            else:
                times[format_time] += 1
        
        df = pd.DataFrame(times.items(), columns=['date', 'transfers'])
        nft_graph = px.bar(df, x='date', y='transfers', color_discrete_sequence=["white"], height=300)
        nft_graph.update_layout({'xaxis_title':'TIME', 'xaxis_color': 'white', 'yaxis_color': 'white', 'yaxis_title':'# of TRANSFERS',
        'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)', 'title_font_color':'white', 'yaxis_showgrid':False})

        # ERC20 token transfers
        response_token = requests.get(f"""https://api.etherscan.io/api?module=account&action=tokentx&address={clean_address}&startblock=0&endblock=999999999&sort=asc&apikey={etherscan_key}""")
        token_transfers = []
        results_token = response_token.json()['result']
        if len(results_token) <= threshold:
            for i in range(len(results_token)):
                if i == 0:
                    token_transfers.append("1.) " + str(results_token[-1]['tokenName']) + " (" + str(results_token[-1]['tokenSymbol']) + ")")
                else:
                    token_transfers.append(f", {i + 1}.) " + str(results_token[-1-i]['tokenName']) + " (" + str(results_token[-1-i]['tokenSymbol']) + ")")
        else:
            for i in range(threshold):
                if i == 0:
                    token_transfers.append("1.) " + str(results_token[-1]['tokenName']) + " (" + str(results_token[-1]['tokenSymbol']) + ")")
                else:
                    token_transfers.append(f", {i + 1}.) " + str(results_token[-1-i]['tokenName']) + " (" + str(results_token[-1-i]['tokenSymbol']) + ")")

        # VISUALIZE ERC20 token transfers
        times = {}
        for i in range(len(results_token)):
            unix = int(results_token[i]['timeStamp'])
            time = epoch_conversion(unix)
            format_time = str(time.year) + "-" + str(time.month) + "-" + str(time.day)
            if format_time not in times:
                times[format_time] = 1
            else:
                times[format_time] += 1
        
        df = pd.DataFrame(times.items(), columns=['date', 'transfers'])
        token_graph = px.bar(df, x='date', y='transfers', color_discrete_sequence=["white"], height=300)
        token_graph.update_layout({'xaxis_title':'TIME', 'xaxis_color': 'white', 'yaxis_color': 'white', 'yaxis_title':'# of TRANSFERS',
        'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)', 'title_font_color':'white', 'yaxis_showgrid':False})
    return display_nft_transfers, nft_transfers, display_nft_graph, nft_graph, display_token_transfers, token_transfers, display_token_graph, token_graph


@app.callback(
    [Output(component_id='nft_images', component_property='children'),
    Output(component_id='display_nft_holdings', component_property='children'),
    Output(component_id='nft_worth_in_usd', component_property='children')],
    [Input(component_id='search', component_property='n_clicks')],
    [State(component_id='address', component_property='value')]
)

def generate_nft_holdings(n_clicks, address):
    """
    Function takes in n_clicks and Ethereum address and outputs
    images of the address's NFT holdings
    """
    if n_clicks == 0 or address is None:
        raise PreventUpdate
    else:
        # App section title
        display_nft_holdings = "NFT HOLDINGS"

        # NFT net worth
        nft_net_worth = 0

        # Cleans and converts address to Checksum Address
        clean_address = address_to_checksum(address)

        response_nft = requests.get(f"""https://api.etherscan.io/api?module=account&action=tokennfttx&address={clean_address}&startblock=0&endblock=999999999&sort=asc&apikey={etherscan_key}""")
        results_nft = response_nft.json()['result']

        # Find NFTs that account still owns
        transfers_in = []
        transfers_out = []
        holdings = []
        for i in range(len(results_nft)):
            if results_nft[i]['to'] == clean_address.lower():
                transfers_in.append((results_nft[i]['contractAddress'], results_nft[i]['tokenID']))
            else:
                transfers_out.append((results_nft[i]['contractAddress'], results_nft[i]['tokenID']))

        for nft in transfers_in:
            if nft not in transfers_out:
                holdings.append(nft)

        # Find the images of the account's NFT holdings
        nft_images = []
        for i in range(len(holdings)):
            contract_address = holdings[i][0]
            contract_tokenID = holdings[i][1]
            try:
                response_nft_image = requests.request("GET", f"https://api.opensea.io/api/v1/asset/{contract_address}/{contract_tokenID}/")
                if response_nft_image:
                    nft_images.append(html.Img(src=response_nft_image.json()['image_preview_url'], style={'height': '10%', 'width': '10%'}))
                if response_nft_image.json()['last_sale']['total_price'] is not None:
                    nft_net_worth += wei_to_ether(int(response_nft_image.json()['last_sale']['total_price']))
            except (IndexError, KeyError, TypeError):
                pass

        nft_worth_in_usd = ether_in_usd(nft_net_worth)

    return nft_images, display_nft_holdings, nft_worth_in_usd


@app.callback(
    [Output(component_id='token_images', component_property='children'),
    Output(component_id='display_token_holdings', component_property='children')],
    [Input(component_id='search', component_property='n_clicks')],
    [State(component_id='address', component_property='value')]
)

def generate_token_holdings(n_clicks, address):
    """
    Function takes in n_clicks and Ethereum address and outputs
    images of the address's ERC20 token holdings
    """
    if n_clicks == 0 or address is None:
        raise PreventUpdate
    else:
        # App section title
        display_token_holdings = "ERC20 HOLDINGS"

        # Cleans and converts address to Checksum Address
        clean_address = address_to_checksum(address)

        # Connect to API to access all token transfers
        response_token = requests.get(f"""https://api.etherscan.io/api?module=account&action=tokentx&address={clean_address}&startblock=0&endblock=999999999&sort=asc&apikey={etherscan_key}""")
        results_token = response_token.json()['result']

        # Find which ER20 tokens the account still owns
        holdings = {}
        for i in range(len(results_token)):
            contract_address = address_to_checksum(results_token[i]['contractAddress'])
            token_symbol = results_token[i]['tokenSymbol']
            token_value = wei_to_ether(int(results_token[i]['value']))

            if results_token[i]['to'] == clean_address.lower():
                if (contract_address, token_symbol) in holdings:
                    holdings[(contract_address, token_symbol)] += token_value
                else:
                    holdings[(contract_address, token_symbol)] = token_value
            else:
                if (contract_address, token_symbol) in holdings:
                    holdings[(contract_address, token_symbol)] -= token_value
                else:
                    holdings[(contract_address, token_symbol)] = -token_value
        
        # Store tokens that account still owns in token_holdings
        token_holdings = []
        for key, val in holdings.items():
            if val > 0:
                token_holdings.append(key[0])

        # Find images of the tokens the account still owns for rendering
        token_images = []
        for address in token_holdings:
            try:
                response_token_image = f"https://assets.trustwalletapp.com/blockchains/ethereum/assets/{address}/logo.png"
                token_images.append(html.Img(src=response_token_image, style={'height': '20%', 'width': '20%'}))
            except (IndexError, KeyError, TypeError):
                pass

    return token_images, display_token_holdings
