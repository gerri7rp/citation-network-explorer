# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 10:17:48 2025

@author: Gerard
"""


import dash
from dash import html, callback, Output, Input, dcc, State, ALL
from utils import queries, data_preparation, common_layout as c_lay, stylesheet
from neo4j import GraphDatabase
from dash.exceptions import PreventUpdate



URI = "bolt://localhost:7687"
AUTH = ("neo4j", "CitationGraph123")
driver = GraphDatabase.driver(URI, auth=AUTH)

TITOL = "Search"
PAGE_NUM = "0"

dash.register_page(__name__, path="/search", name=TITOL)


nodes_list, edges_list = [], []
is_options_dropdown_shown = False



def consulta(nom, tipus_node, tipus_veins): 
    records = queries.obtenir_node_i_veins(driver, nom, tipus_node, tipus_veins)
    print(records)
    
    if len(records) > 0:
        nodes_list, edges_list = data_preparation.prepare_nodes_and_edges(records)

        return nodes_list, edges_list
        
    else:
        return [], []
    


layout = html.Div(
    children=[
        # Columna izquierda: Menú lateral
        html.Div([
            c_lay.go_back_to_menu_button,
            html.H1(TITOL), 
            html.P("Tipus de node a cercar:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id=f'graph-selection{PAGE_NUM}',
                placeholder='Tipus de node',
                clearable=False,
                options=[
                    {"label": "Articles", "value": "Article"},
                    {"label": "Autors", "value": "Autor"},
                    {"label": "Camp Estudi", "value": "Camp_Estudi"}
                ],
                style={'width': '10vw'}
            ),

            html.P("Nom del node:", style={'fontWeight': 'bold'}),
            html.Div([
                dcc.Input(id=f'input{PAGE_NUM}', type='text', placeholder='Tu texto aquí...', style={'width': '13vw'}),
                html.Button("🔍", id=f'btn{PAGE_NUM}', n_clicks=0, style={'marginLeft': '5px'}),
                html.Div(id=f'dropdown-container{PAGE_NUM}', children=[], style = {}),
                ], style={'position': 'relative', 'marginLeft': '5px'}),
            html.P("Tipus de veïns a mostrar:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id=f'neigh-selection{PAGE_NUM}',
                placeholder='Tipus de veïns',
                clearable=False,
                options=[
                    {"label": "Articles", "value": "Article"},
                    {"label": "Autors", "value": "Autor"},
                    {"label": "Camp Estudi", "value": "Camp_Estudi"}
                ],
                style={'width': '10vw'}
            ),
            c_lay.obtain_search_button(PAGE_NUM),
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
            dcc.Store(id=f'graph_summary_store_1_{PAGE_NUM}', data=None),
            dcc.Store(id=f'graph_summary_store_2_{PAGE_NUM}', data=None),
            dcc.Store(id=f'dropdown_data_storing-show{PAGE_NUM}', data=[]),  
            dcc.Store(id=f'dropdown_data_storing-hide{PAGE_NUM}', data=[]),
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




@callback(
    Output(f'neigh-selection{PAGE_NUM}', 'options'),
    Input(f'graph-selection{PAGE_NUM}', 'value'),
    prevent_initial_call=True
)
def update_neigh_dropdown(tipus_node):
    options=[
        {"label": "Articles", "value": "Article"},
        {"label": "Autors", "value": "Autor"},
        {"label": "Camp Estudi", "value": "Camp_Estudi"}
    ]
    
    if tipus_node == "Autor":
        options.pop(2)

    elif tipus_node == "Camp_Estudi":
        options.pop(1)
        options.pop(1)
        
    return options


@callback(
    Output(f'cytoscape-update-layout_{PAGE_NUM}', 'layout'),
    Input('dropdown-update-layout', 'value'))
def update_layout(layout):
    return {'name' : layout, 'animate' : True}



@callback(
    Output(f"graph_component{PAGE_NUM}", 'children'),
    Output(f'graph_summary_store_1_{PAGE_NUM}', "data"),
    Input(f'search-button_{PAGE_NUM}', 'n_clicks'),
    State(f'input{PAGE_NUM}', 'value'),
    State(f'graph-selection{PAGE_NUM}', 'value'),
    State(f'neigh-selection{PAGE_NUM}', 'value'),
    prevent_initial_call=True
)
def mostrar_graf(n_clicks, valor,  tipus_node, tipus_veins):
    global nodes_list, edges_list
    
    if n_clicks == 0:
        raise PreventUpdate
        
    if not valor:
        return dash.no_update  # no hacer nada si los inputs están vacíos

    nodes_list, edges_list = consulta(valor, tipus_node, tipus_veins)
    elements_list = nodes_list + edges_list
    
    
    if len(elements_list) == 0:
        return None, None
        
    children = c_lay.obtain_graph_component(PAGE_NUM, elements_list, stylesheet.stylesheet)
        
    graph_summary_store_1 = [len(nodes_list), len(edges_list)]
    
    return children, graph_summary_store_1


@callback(
    Output(f'dropdown_data_storing-show{PAGE_NUM}', 'data'), 
    Input(f'btn{PAGE_NUM}', 'n_clicks'),
    State(f'input{PAGE_NUM}', 'value'),
    State(f'dropdown_data_storing-show{PAGE_NUM}', 'data'),  
    State(f'graph-selection{PAGE_NUM}', 'value'),
    prevent_initial_call=True
)
def mostrar_opciones(n_clicks, value_input, dropdown_data_storing, tipus_node):
    print("hhelo mostrar_opciones")
    
    global is_options_dropdown_shown
    is_options_dropdown_shown = True
    
    if n_clicks == 0:
        raise PreventUpdate()
        
    if not value_input:
        raise PreventUpdate() 
    
    if not value_input.strip(): # Si no contiene algun caracter != espacio en blanco
        raise PreventUpdate() 
        
    print("\n\nVALUE INPUT:", value_input)
    
    records = queries.text_search(driver, tipus_node, value_input, limit=10)
        
    if not records:
        raise PreventUpdate()
    
    nodes_list = []    
    for node in records:
         nodes_list.append( data_preparation.prepare_nodes(node, [20]) )
         
    resultados = [(node[0]["data"]["nom"], node[0]["data"]["id"]) for node in nodes_list]
    
    opciones = [
        html.Div(
            children=resultado[0], 
            title = resultado[1],
            id={'type': f"dropdown-option{PAGE_NUM}", 'index': f'dropdown-options{PAGE_NUM}'},
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
    Output(f'input{PAGE_NUM}', 'value'),
    Output(f'dropdown_data_storing-hide{PAGE_NUM}', 'data'), 
    Input({'type': f'dropdown-option{PAGE_NUM}', 'index': ALL}, 'n_clicks'),
    State({'type': f'dropdown-option{PAGE_NUM}', 'index': ALL}, 'children'),
    State(f'dropdown_data_storing-hide{PAGE_NUM}', 'data'),  
    prevent_initial_call=True
)
def seleccionar_opcion_dropdown(n_clicks_list, children_list, dropdown_data_storing):
    print("hhelo seleccionar_opcion_dropdown")
    
    global is_options_dropdown_shown
    is_options_dropdown_shown = False
    
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    # Encuentra el índice de la opción clicada
    for i, n in enumerate(n_clicks_list):
        if n:
            valor_seleccionado = children_list[i]  # Texto clicado
            break
    else:
        raise PreventUpdate

    # Oculta el contenedor
    estilo_oculto = {'display': 'none'}
    
    dropdown_data_storing = [None, estilo_oculto]

    return valor_seleccionado, dropdown_data_storing
    

    

@callback(
    Output(f'dropdown-container{PAGE_NUM}', 'children'),
    Output(f'dropdown-container{PAGE_NUM}', 'style'),
    Input(f'dropdown_data_storing-show{PAGE_NUM}', 'data'),  
    Input(f'dropdown_data_storing-hide{PAGE_NUM}', 'data'),
    prevent_initial_call=True
)
def cambiar_config_dropdown_opciones(dropdown_data_storing_show, dropdown_data_storing_hide):
    print("hello cambiar_config_dropdown_opciones\n")

    global is_options_dropdown_shown
    
    if is_options_dropdown_shown == True:
        return dropdown_data_storing_show[0], dropdown_data_storing_show[1]
    else:
        return dropdown_data_storing_hide[0], dropdown_data_storing_hide[1]
    


@callback(
    Output(f'info-box{PAGE_NUM}', 'children'),
    Input(f'cytoscape-update-layout_{PAGE_NUM}', 'selectedNodeData')
)
def display_node_data(selected_node):
    return c_lay.selected_node_general_function(selected_node)



@callback(
    Output(f"graph_component{PAGE_NUM}", 'children', allow_duplicate=True),
    Output(f"leyenda{PAGE_NUM}", "children"),
    Input(f"graph_component{PAGE_NUM}", 'children'),
    prevent_initial_call=True
)
def update_graph_stylesheet(children):      
    print("hello update")
    global nodes_list
    
    if not children:
        raise PreventUpdate()
    
    dynamic_style, leyenda = c_lay.obtain_dynamic_styles("etiqueta", nodes_list)
    leyenda = c_lay.generate_legend_component(leyenda)
        
    children["props"]["stylesheet"] += dynamic_style
    
    return children, leyenda



@callback(
    Output(f"graph-summary_{PAGE_NUM}", "children"),
    Input(f'graph_summary_store_1_{PAGE_NUM}', "data"),
    Input(f'graph_summary_store_2_{PAGE_NUM}', "data"),
    prevent_initial_call=True
)
def update_graph_summary(graph_summary_1, graph_summary_2):    
    if graph_summary_2:
        num_nodes = graph_summary_2[0]
        num_edges = graph_summary_2[1]
        
    elif graph_summary_1:
        num_nodes = graph_summary_1[0]
        num_edges = graph_summary_1[1]
        
    else:
        raise PreventUpdate()
        
    return c_lay.obtain_summary_text(num_nodes, num_edges, "Autors")
