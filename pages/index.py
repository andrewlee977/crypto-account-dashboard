# Imports from 3rd party libraries
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

# Imports from this application
from app import app

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
        dcc.Input(id='search'),
        html.Br(),
        html.Br(),
        dcc.Link(dbc.Button('Search Address', color='primary'), href='/dashboard')
    ],
    md=4,
)

gapminder = px.data.gapminder()
# fig = px.scatter(gapminder.query("year==2007"), x="gdpPercap", y="lifeExp", size="pop", color="continent",
#            hover_name="country", log_x=True, size_max=60)

column2 = dbc.Col(
    [
        # dcc.Graph(figure=fig),
        html.Img(src="assets/crypto-dashboard.jpeg", width='725px', height='400px')
    ]
)

layout = dbc.Row([column1, column2])