# -*- coding: utf-8 -*-
"""
Created on Sat May 17 17:48:02 2025

@author: Gerard
"""

from dash import Dash, html, dcc
import dash
import webbrowser


app = Dash(__name__, use_pages=True, external_stylesheets=['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css'], 
           suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(dash.page_container)
])

if __name__ == "__main__":
    app.run(debug=False)
    webbrowser.open_new("http://127.0.0.1:8050/")

