# Imports from 3rd party libraries
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Imports from this application
from app import app

# 1 column layout
# https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout
# column1 = dbc.Col(
#     [
layout = html.Div([
    dcc.Markdown(
        """

        ## Insights
        # Hello

        """
    )], style={'text-align': 'center'}
)
#     ],
# )

# layout = dbc.Row([column1])