# -*- coding: utf-8 -*-
"""
Created on Sat May 17 17:48:35 2025

@author: Gerard
"""

import dash
from dash import html, callback, Output, Input, dcc, State, ALL
from utils import queries, data_preparation, common_layout as c_lay, stylesheet
from neo4j import GraphDatabase
from dash.exceptions import PreventUpdate



URI = "bolt://localhost:7690"
AUTH = ("neo4j", "CitationGraph123")
driver = GraphDatabase.driver(URI, auth=AUTH)

TITOL = "Camí més curt"
PAGE_NUM = "1"

dash.register_page(__name__, path="/cami-mes-curt", name=TITOL)


is_options_dropdown_1_shown = False
is_options_dropdown_2_shown = False



def consulta(tipus_graf, id_1, id_2):
    if tipus_graf == "Articles":
        records = queries.shortest_path_articles(driver, id_1, id_2)   
    
    elif tipus_graf == "Autors":
        records = queries.shortest_path_autors(driver, id_1, id_2)   
        
    
    if len(records) > 0:
        nodes_list, edges_list = data_preparation.prepare_nodes_and_edges(records, isShortestPath = True)
        
        nodes_list[0]["data"]["positionInPath"] = "Start"
        nodes_list[-1]["data"]["positionInPath"]  = "End"
            
        return nodes_list, edges_list
        
    else:
        return [], []
    

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
                style={'width': '10vw'}
            ),
            html.Div(id='contenedor-input-data'),
            html.Pre(id="graph-summary", style = c_lay.graph_summary_style),
            c_lay.obtain_info_box_component(PAGE_NUM),
            dcc.Store(id='dropdown_data_storing-show-1', data=[]),  
            dcc.Store(id='dropdown_data_storing-hide-1', data=[]),
            dcc.Store(id='dropdown_data_storing-show-2', data=[]),  
            dcc.Store(id='dropdown_data_storing-hide-2', data=[]),
            dcc.Store(id="object-start-id", data=None),
            dcc.Store(id="object-end-id", data=None)
        ],
        style=c_lay.left_column_style),

        # Columna derecha: Grafo centrado
        html.Div([
            c_lay.graph_layout_selector,
            c_lay.obtain_graph_component(PAGE_NUM, [], stylesheet.stylesheet)
            ], 
            style = c_lay.right_column_style
        )
    ],
    style = c_lay.screen_style, 
)

@callback(
    Output(f'cytoscape-update-layout_{PAGE_NUM}', 'elements'),
    Output("graph-summary", "children"),
    Input(f'search-button_{PAGE_NUM}', 'n_clicks'),
    State("graph-selection", "value"),
    State("object-start-id", "data"),
    State("object-end-id", "data"),
    prevent_initial_call=True
)
def mostrar_graf(n_clicks, tipus_graf, id1, id2):    
    if n_clicks == 0:
        raise PreventUpdate
            
    if not id1 or not id2:
        return dash.no_update  # no hacer nada si los inputs están vacíos
    
    if id1 == id2:
        return dash.no_update
    
    nodes_list, edges_list = consulta(tipus_graf, id1, id2)
    elements_list = nodes_list + edges_list
        
    summary_text = c_lay.obtain_summary_text(len(nodes_list), len(edges_list), tipus_graf) 

    return elements_list, summary_text

  

@callback(
    Output('contenedor-input-data', 'children'),
    Input('graph-selection', 'value')
)
def mostrar_input(valor):
    if valor == 'Articles':
        text1 = "Títol Article Origen:"
        text2 = "Títol Article Destí:"
    
    elif valor == "Autors":
        text1 = "Nom Autor Origen:"
        text2 = "Nom Autor Destí:"
        
    else:
        return html.Div()
    
    return html.Div([
                html.P(text1, style={'fontWeight': 'bold', 'color' : 'blue'}),
                html.Div([
                    dcc.Input(id='input-1', type='text', value = "", placeholder='Tu texto aquí...', style={'width': '13vw'}),
                    html.Button("🔍", id='btn-1', n_clicks=0, style={'marginLeft': '5px'})
                    ], style={'marginLeft': '5px'}),
                html.Div(id='dropdown-container-1', children=[], style = {}),
                html.P(text2, style={'fontWeight': 'bold', 'color' : 'green'}),
                html.Div([
                    dcc.Input(id='input-2', type='text', value = "", placeholder='Tu texto aquí...', style={'width': '13vw'}),
                    html.Button("🔍", id='btn-2', n_clicks=0, style={'marginLeft': '5px'})
                    ], style={'marginLeft': '5px'}),
                html.Div(id='dropdown-container-2', children=[], style = {}),
                c_lay.obtain_search_button(PAGE_NUM), 
        ], style={'marginTop': '15px'})
    

@callback(Output(f'cytoscape-update-layout_{PAGE_NUM}', 'layout'),
              Input('dropdown-update-layout', 'value'))
def update_layout(layout):
    return {'name' : layout, 'animate' : True}


@callback(
    Output(f'info-box{PAGE_NUM}', 'children'),
    Input(f'cytoscape-update-layout_{PAGE_NUM}', 'selectedNodeData'),
    prevent_initial_call=True
)
def display_node_data(selected_node):
    return c_lay.selected_node_general_function(selected_node)


@callback(
    Output('dropdown-container-1', 'children'),
    Output('dropdown-container-1', 'style'),
    Input('dropdown_data_storing-show-1', 'data'),  
    Input('dropdown_data_storing-hide-1', 'data'),
    prevent_initial_call=True
)
def cambiar_config_dropdown_opciones_1(dropdown_data_storing_show, dropdown_data_storing_hide):
    print("hello cambiar_config_dropdown_opciones\n")

    global is_options_dropdown_1_shown
    
    if is_options_dropdown_1_shown == True:
        return dropdown_data_storing_show[0], dropdown_data_storing_show[1]
    else:
        return dropdown_data_storing_hide[0], dropdown_data_storing_hide[1]
    
    
    
@callback(
    Output('dropdown-container-2', 'children'),
    Output('dropdown-container-2', 'style'),
    Input('dropdown_data_storing-show-2', 'data'),  
    Input('dropdown_data_storing-hide-2', 'data'),
    prevent_initial_call=True
)
def cambiar_config_dropdown_opciones_2(dropdown_data_storing_show, dropdown_data_storing_hide):
    print("hello cambiar_config_dropdown_opciones\n")

    global is_options_dropdown_2_shown
    
    if is_options_dropdown_2_shown == True:
        return dropdown_data_storing_show[0], dropdown_data_storing_show[1]
    else:
        return dropdown_data_storing_hide[0], dropdown_data_storing_hide[1]
    

def codigo_compartido_mostrar_opciones(n_clicks, value_input, tipus_graf, dropdown_name):
    if n_clicks == 0:
        raise PreventUpdate()
        
    if not value_input:
        raise PreventUpdate() 
    
    if not value_input.strip(): # Si no contiene algun caracter != espacio en blanco
        raise PreventUpdate() 
        
    print("\n\nVALUE INPUT:", value_input)
    
    records = queries.text_search(driver, tipus_graf[:-1], value_input, limit=10)
    
    if not records:
        print("No results bro")
        raise PreventUpdate()
    
    nodes_list = []    
    for node in records:
         nodes_list.append( data_preparation.prepare_nodes(node, [20]) )
         
    resultados = [(node[0]["data"]["nom"], node[0]["data"]["id"]) for node in nodes_list]
    
    opciones = [
        html.Div(
            children=resultado[0], 
            title = resultado[1],
            id={'type': dropdown_name, 'index': 'dropdown-options'},
            style={
                'padding': '5px 10px',
                'cursor': 'pointer',
                'borderBottom': '1px solid #eee'
            }
        )
        for resultado in resultados
    ]

    return [opciones, c_lay.options_dropdown_style]

    
@callback(
    Output('dropdown_data_storing-show-1', 'data'), 
    Input('btn-1', 'n_clicks'),
    State('input-1', 'value'),
    State('dropdown_data_storing-show-1', 'data'),  
    State("graph-selection", "value"),
    prevent_initial_call=True
)
def mostrar_opciones_1(n_clicks, value_input, dropdown_data_storing, tipus_graf):
    global is_options_dropdown_1_shown
    is_options_dropdown_1_shown = True
    
    print("hhelo mostrar_opciones")
    
    dropdown_data_storing = codigo_compartido_mostrar_opciones(n_clicks, value_input, tipus_graf, 'dropdown-option-1')

    return dropdown_data_storing

  
@callback(
    Output('dropdown_data_storing-show-2', 'data'), 
    Input('btn-2', 'n_clicks'),
    State('input-2', 'value'),
    State('dropdown_data_storing-show-2', 'data'), 
    State("graph-selection", "value"),
    prevent_initial_call=True
)
def mostrar_opciones_2(n_clicks, value_input, dropdown_data_storing, tipus_graf):
    global is_options_dropdown_2_shown
    is_options_dropdown_2_shown = True
    
    print("hhelo mostrar_opciones")
    
    dropdown_data_storing = codigo_compartido_mostrar_opciones(n_clicks, value_input, tipus_graf, 'dropdown-option-2')

    return dropdown_data_storing




def codigo_compartido_seleccionar_opcion_dropdown(n_clicks_list, children_list, titles_list):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    # Encuentra el índice de la opción clicada
    for i, n in enumerate(n_clicks_list):
        if n:
            valor_seleccionado = children_list[i]  # Texto clicado
            id_seleccionado = titles_list[i]
            break
    else:
        raise PreventUpdate

    # Oculta el contenedor
    estilo_oculto = {'display': 'none'}
    
    dropdown_data_storing = [None, estilo_oculto]

    return valor_seleccionado, dropdown_data_storing, id_seleccionado


@callback(
    Output('input-1', 'value'),
    Output('dropdown_data_storing-hide-1', 'data'), 
    Output("object-start-id", "data"),
    Input({'type': 'dropdown-option-1', 'index': ALL}, 'n_clicks'),
    State({'type': 'dropdown-option-1', 'index': ALL}, 'children'),
    State({'type': 'dropdown-option-1', 'index': ALL}, 'title'),
    State('dropdown_data_storing-hide-1', 'data'),  
    prevent_initial_call=True
)
def seleccionar_opcion_dropdown_1(n_clicks_list, children_list, titles_list, dropdown_data_storing):
    print("hhelo seleccionar_opcion_dropdown")
    
    global is_options_dropdown_1_shown
    is_options_dropdown_1_shown = False
    
    return codigo_compartido_seleccionar_opcion_dropdown(n_clicks_list, children_list, titles_list)


@callback(
    Output('input-2', 'value'),
    Output('dropdown_data_storing-hide-2', 'data'), 
    Output("object-end-id", "data"),
    Input({'type': 'dropdown-option-2', 'index': ALL}, 'n_clicks'),
    State({'type': 'dropdown-option-2', 'index': ALL}, 'children'),
    State({'type': 'dropdown-option-2', 'index': ALL}, 'title'),
    State('dropdown_data_storing-hide-2', 'data'),  
    prevent_initial_call=True
)
def seleccionar_opcion_dropdown_2(n_clicks_list, children_list, titles_list, dropdown_data_storing):
    print("hhelo seleccionar_opcion_dropdown")
    
    global is_options_dropdown_2_shown
    is_options_dropdown_2_shown = False
    
    return codigo_compartido_seleccionar_opcion_dropdown(n_clicks_list, children_list, titles_list)


