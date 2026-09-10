# -*- coding: utf-8 -*-
"""
Created on Sat May 17 19:26:23 2025

@author: Gerard
"""

import dash
from dash import html, callback, Output, Input, dcc, State
from utils import queries, data_preparation, common_layout as c_lay, stylesheet
from neo4j import GraphDatabase
from dash.exceptions import PreventUpdate
import random
import dash_cytoscape as cyto




URI = "bolt://localhost:7687"
AUTH = ("neo4j", "CitationGraph123")
driver = GraphDatabase.driver(URI, auth=AUTH)

TITOL = "Top Communities"
PAGE_NUM = "3"
isFirstGraphUpdate = True
graphType = None

dash.register_page(__name__, path="/top-communities", name=TITOL)

graphs_list = []


def consulta(tipus_graf, algorithm, num_comunitats): 
    if tipus_graf == "Articles": 
        tipus_graf = "graph-articles"
        
    elif tipus_graf == "Autors":
        tipus_graf = "graph-autors"
        
        
    records = queries.execute_community_algorithm(driver, tipus_graf, algorithm, num_comunitats)

    if len(records) > 0:
        graphs_list = []
        for record in records:
            nodes_list = data_preparation.prepare_nodes(record["nodes"], sizes = [20] * len(record["nodes"]))
            edges_list = data_preparation.prepare_edges(record["edges"])
            
            graphs_list.append( {"nodes" : nodes_list, "edges" : edges_list} )
            
        return graphs_list[0]["nodes"], graphs_list[0]["edges"], graphs_list
        
    else:
        return [], [], []



layout = html.Div(
    children=[
        # Columna izquierda: Menú lateral
        html.Div([
            c_lay.go_back_to_menu_button,
            html.H1(TITOL), 
            dcc.Dropdown(
                id='graph-selection',
                placeholder='Tipus de node',
                clearable=False,
                options=[
                    {"label": "Articles", "value": "Articles"},
                    {"label": "Autors", "value": "Autors"}
                ],
                style={'width': '14vw'}
            ),
            dcc.Dropdown(
                id='algorithm-selection',
                placeholder='Algoritme',
                clearable=False,
                options=[
                    {"label": "Weakly Connected Components", "value": "WCC"},
                    {"label": "Label Propagation", "value": "Label Prop"},
                    {"label": "Louvain Modularity", "value": "Louvain Mod"}
                ],
                style={'width': '14vw', 'marginTop': '5px'}
            ),
            html.P("Nombre de comunitats:", style={'fontWeight': 'bold'}),
            dcc.Input(id="input-n-comunitats", type='text', placeholder='Tu texto aquí...', value="5", style={'width': '4vw'}),
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
                html.Div(id=f"leyenda{PAGE_NUM}"),
                c_lay.obtain_info_box_component(PAGE_NUM),
            ],
            style={
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '10px'  # espacio entre el resumen y la leyenda
            }),
        ],
        style=c_lay.left_column_style),

        # Columna derecha: Grafo centrado
        html.Div([
            c_lay.graph_layout_selector,
            html.Div(id=f"graph_component{PAGE_NUM}"),
            html.Div(id='community-index-component'), 
            html.Div(id='flechas_component'),
            dcc.Store(id='current-community-index', data=0)
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
    Output(f"graph-summary_{PAGE_NUM}", "children", allow_duplicate=True),
    Output('community-index-component', "children"),
    Output('flechas_component', 'children'),
    Output(f'color-selection{PAGE_NUM}', 'value'),
    Output(f'color-selection{PAGE_NUM}', 'options'),
    Input(f'search-button_{PAGE_NUM}', 'n_clicks'),
    State("graph-selection", "value"),
    State("algorithm-selection", "value"),
    State("input-n-comunitats", 'value'),
    prevent_initial_call=True
)
def mostrar_graf(n_clicks, tipus_graf, algorithm, num_comunitats):
    global nodes_list, edges_list, graphs_list, isFirstGraphUpdate, graphType
    
    if n_clicks == 0:
        raise PreventUpdate
        
    if not tipus_graf or not num_comunitats:
        return dash.no_update  # no hacer nada si los inputs están vacíos

    nodes_list, edges_list, graphs_list = consulta(tipus_graf, algorithm, int(num_comunitats))
    elements_list = nodes_list + edges_list
    
    if len(elements_list) == 0:
        return None, None, None
        
    children = c_lay.obtain_graph_component(PAGE_NUM, elements_list, stylesheet.stylesheet), 
    community_index_children = c_lay.obtain_community_index_label(graphs_list)
    flechas_children = c_lay.flechas_component
    graph_summary_store_1 = c_lay.obtain_summary_text(len(nodes_list), len(edges_list), tipus_graf)
    
    isFirstGraphUpdate = True
    
    opcions = [
        {"label": "Tipus Node", "value": "etiqueta"},
        {"label": "Organització Autor", "value": "organitzacio"},
    ]
    
    if tipus_graf == "Articles":
        opcions.pop(1)
        
         
    graphType = tipus_graf
    
    return children, graph_summary_store_1, community_index_children, flechas_children, "etiqueta", opcions




@callback(
    Output(f"graph_component{PAGE_NUM}", 'children', allow_duplicate=True),
    Output(f"leyenda{PAGE_NUM}", "children"),
    Input(f'color-selection{PAGE_NUM}', 'value'),
    Input('current-community-index', 'data'),
    State(f"graph_component{PAGE_NUM}", 'data'),
    State(f"graph_component{PAGE_NUM}", 'children'),
    prevent_initial_call=True
)
def update_graph_stylesheet(color_attribute, current_index, graph_data, children):        
    if not children:
        raise PreventUpdate()

    comunidad = graphs_list[current_index]
    

    dynamic_style, leyenda = c_lay.obtain_dynamic_styles(color_attribute, comunidad["nodes"])
    leyenda = c_lay.generate_legend_component(leyenda)
        
    
    children[0]["props"]["stylesheet"] += dynamic_style
    
    return children, leyenda




@callback(
        Output(f'cytoscape-update-layout_{PAGE_NUM}', 'elements'),
        Output('current-community-index', 'data'),
        Output('community-index-label', 'children'),
        Output(f"graph-summary_{PAGE_NUM}", "children", allow_duplicate=True),
        Input('btn-prev', 'n_clicks'),
        Input('btn-next', 'n_clicks'),
        State('current-community-index', 'data'),
        prevent_initial_call=True
)
def update_graph(prev_clicks, next_clicks, current_index):    
    ctx = dash.callback_context

    global isFirstGraphUpdate, graphType

    if isFirstGraphUpdate:
        current_index = 0
     
    if not ctx.triggered:
        comunidad = graphs_list[current_index]
        elements = comunidad['nodes'] + comunidad['edges']
        label = f"Comunitat {current_index + 1} de {len(graphs_list)}"
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
     
                
    if button_id == 'btn-prev':
        if current_index == 0:
            raise PreventUpdate()
        current_index = max(0, current_index - 1)
       
    elif button_id == 'btn-next':
        if current_index == len(graphs_list) - 1:
            raise PreventUpdate()
        current_index = min(len(graphs_list) - 1, current_index + 1)
    

    isFirstGraphUpdate = False
    comunidad = graphs_list[current_index]
    elements = comunidad['nodes'] + comunidad['edges']
    label = f"Comunitat {current_index + 1} de {len(graphs_list)}"
    
    graph_summary_store_2 = c_lay.obtain_summary_text(len(comunidad['nodes']), len(comunidad['edges']), graphType)

    return elements, current_index, label, graph_summary_store_2


@callback(
    Output(f'info-box{PAGE_NUM}', 'children'),
    Input(f'cytoscape-update-layout_{PAGE_NUM}', 'selectedNodeData')
)
def display_node_data(selected_node):
    return c_lay.selected_node_general_function(selected_node)


@callback(
    Output("legend-content", "style"),
    Input("legend-toggle", "n_clicks"),
    State("legend-content", "style"),
    prevent_initial_call=True
)
def toggle_legend(n_clicks, current_style):
    if current_style and current_style.get("display") == "none":
        return {"display": "block"}
    else:
        return {"display": "none"}