# -*- coding: utf-8 -*-
"""
Created on Tue May 27 17:48:06 2025

@author: Gerard
"""

import dash
from dash import html, callback, Output, Input, dcc, State
from utils import queries, data_preparation, common_layout as c_lay, stylesheet
from neo4j import GraphDatabase
from dash.exceptions import PreventUpdate
import numpy as np


URI = "bolt://localhost:7687"
AUTH = ("neo4j", "CitationGraph123")
driver = GraphDatabase.driver(URI, auth=AUTH)

TITOL = "Node Centrality"
PAGE_NUM = "4"
nodes_list = []

dash.register_page(__name__, path="/node-centrality", name=TITOL)


def consulta(tipus_graf, algorithm):
    if tipus_graf == "Articles": 
        tipus_graf = "graph-articles"
        
    elif tipus_graf == "Autors":
        tipus_graf = "graph-autors"
        
    records = queries.execute_centrality_algorithm(driver, tipus_graf, algorithm)
    
    centralities_array = np.array(records[0][2])
    
    min_centrality = np.min(centralities_array)
    max_centrality = np.max(centralities_array)
        
    sizes_array = (centralities_array - min_centrality) / (max_centrality - min_centrality) * (200 - 20) + 20
    
    if len(records) > 0:
        print("\nSi hay resultados")
        
        nodes_list = data_preparation.prepare_nodes(nodes = records[0][0], sizes = sizes_array.tolist(), centralities = records[0][2])
        edges_list = data_preparation.prepare_edges(edges = records[0][1])
        return nodes_list, edges_list
        
    else:
        print("\nNo hay resultados")
        return [], []
    
    

layout = html.Div(
    children=[
        # Columna izquierda: Menú lateral
        html.Div([
            c_lay.go_back_to_menu_button,
            html.H1(TITOL),
            dcc.Dropdown(
                id=f'graph-selection{PAGE_NUM}',
                placeholder='Tipus de node',
                clearable=False,
                options=[
                    {"label": "Articles", "value": "Articles"},
                    {"label": "Autors", "value": "Autors"}                ],
                style={'width': '14vw'}
            ),
            dcc.Dropdown(
                id='algorithm-selection',
                placeholder='Algoritme',
                clearable=False,
                options=[
                    {"label": "Page Rank", "value": "Page Rank"},
                    {"label": "Betweenness Centrality", "value": "Betweenness Centrality"},
                ],
                style={'width': '14vw', 'marginTop': '5px'}
            ),
            c_lay.obtain_search_button(PAGE_NUM),
            html.P("Pintar nodes segons:"),
            dcc.Dropdown(
                id=f'color-selection{PAGE_NUM}',
                value='etiqueta',
                clearable=False,
                options=[
                    {"label": "Tipus Node", "value": "etiqueta"},
                    {"label": "Organització Autor", "value": "organitzacio"},
                ],
                style={'width': '14vw'}
            ),
            html.Div([
                html.Pre(id=f"graph-summary_{PAGE_NUM}", style=c_lay.graph_summary_style),
                html.Div(id=f"leyenda{PAGE_NUM}")
            ],
            style={
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '10px'  # espacio entre el resumen y la leyenda
            }),
            c_lay.obtain_info_box_component(PAGE_NUM)
        ],
        style=c_lay.left_column_style),

        # Columna derecha: Grafo centrado
        html.Div([
            c_lay.graph_layout_selector,
            html.Div(id=f"graph_component{PAGE_NUM}"),
            ], 
            style = c_lay.right_column_style
        )
    ],
    style = c_lay.screen_style, 
)



@callback(Output(f'cytoscape-update-layout_{PAGE_NUM}', 'layout'),
              Input('dropdown-update-layout', 'value'))
def update_layout(layout):
    return {'name' : layout, 'animate' : True}



@callback(
    Output(f"graph_component{PAGE_NUM}", 'children', allow_duplicate=True),
    Output(f"graph-summary_{PAGE_NUM}", "children"),
    Output(f'color-selection{PAGE_NUM}', 'value'),
    Output(f'color-selection{PAGE_NUM}', 'options'),
    Input(f'search-button_{PAGE_NUM}', 'n_clicks'),
    State(f'graph-selection{PAGE_NUM}', "value"),
    State("algorithm-selection", "value"),
    prevent_initial_call=True
)
def mostrar_graf(n_clicks, tipus_graf, algorithm):
    global nodes_list
    
    if n_clicks == 0:
        raise PreventUpdate
        
    if not tipus_graf:
        return dash.no_update  # no hacer nada si los inputs están vacíos

    nodes_list, edges_list = consulta(tipus_graf, algorithm)
    elements_list = nodes_list + edges_list
    
    children = c_lay.obtain_graph_component(PAGE_NUM, elements_list, stylesheet.stylesheet), 
    
    summary_text = c_lay.obtain_summary_text(len(nodes_list), len(edges_list), tipus_graf)
    
    opcions = [
        {"label": "Tipus Node", "value": "etiqueta"},
        {"label": "Organització Autor", "value": "organitzacio"},
    ]
    
    if tipus_graf == "Articles":
        opcions.pop(1)
        
    print("Dades carregades")
        
    
    return children, summary_text, "etiqueta", opcions



@callback(
    Output(f'info-box{PAGE_NUM}', 'children'),
    Input(f'cytoscape-update-layout_{PAGE_NUM}', 'selectedNodeData'),
    prevent_initial_call=True
)
def display_node_data(selected_node):
    return c_lay.selected_node_general_function(selected_node)


@callback(
    Output(f"graph_component{PAGE_NUM}", 'children', allow_duplicate=True),
    Output(f"leyenda{PAGE_NUM}", "children"),
    Input(f'color-selection{PAGE_NUM}', 'value'),
    Input(f"graph_component{PAGE_NUM}", 'children'),
    prevent_initial_call=True
)
def update_graph_stylesheet(color_attribute, children):      
    print("hello update")
    global nodes_list
    
    if not children:
        raise PreventUpdate()
    
    dynamic_style, leyenda = c_lay.obtain_dynamic_styles(color_attribute, nodes_list)
    leyenda = c_lay.generate_legend_component(leyenda)
    
    children[0]["props"]["stylesheet"] += dynamic_style
    
    return children, leyenda
