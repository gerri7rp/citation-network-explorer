# -*- coding: utf-8 -*-
"""
Created on Sat May 17 17:46:53 2025

@author: Gerard
"""


import dash
from dash import html, dcc

dash.register_page(__name__, path="/", name="Home")

# Estilo de los botones
button_style = {
    'fontSize': '16px',
    'padding': '12px 24px',
    'border': 'none',
    'borderRadius': '8px',
    'backgroundColor': '#2c3e50',
    'color': 'white',
    'cursor': 'pointer',
    'transition': '0.3s',
    'width': '100%',
    'textAlign': 'center'
}

# Layout
layout = html.Div([
    html.Div([
        html.H1("Citation Network Explorer", style={
            'textAlign': 'center',
            'color': '#2c3e50',
            'marginBottom': '40px',
            'cursor': 'default'  # 👈 evita el cursor de texto
        }),

        html.Div([
            dcc.Link(html.Button("Search", style=button_style), href="/search"),
            dcc.Link(html.Button("Shortest Path", style=button_style), href="/shortest-path"),
            dcc.Link(html.Button("Research Field Evolution", style=button_style), href="/field-evolution"),
            dcc.Link(html.Button("Top Communities", style=button_style), href="/top-communities"),
            dcc.Link(html.Button("Node Centrality", style=button_style), href="/node-centrality")
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '20px',
            'alignItems': 'stretch',
            'width': '100%',
            'cursor': 'default'  # 👈 evita el cursor de texto aquí también
        })
    ], style={
        'maxWidth': '400px',
        'width': '90%',
        'margin': '0 auto',
        'padding': '60px 30px',
        'backgroundColor': '#f8f9fa',
        'borderRadius': '16px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.1)',
        'cursor': 'default'  # 👈 también aquí
    })
], style={
    'height': '100vh',
    'width': '100vw',
    'display': 'flex',
    'justifyContent': 'center',
    'alignItems': 'center',
    'background': 'linear-gradient(to right, #ece9e6, #ffffff)',
    'cursor': 'default'  # 👈 y aquí
})
