# -*- coding: utf-8 -*-
"""
Created on Sat May 17 19:06:40 2025

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

TITOL = "Evolució Camp d'Estudi"
PAGE_NUM = "2"

dash.register_page(__name__, path="/evolucio-camp-estudi", name=TITOL)


nodes_list, edges_list, nodes_leyenda = [], [], []
is_options_dropdown_shown = False


def consulta(nom_camp_estudi): 
    records = queries.evolucio_camp_estudi(driver, nom_camp_estudi)
    
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
            html.P("Nom camp d'estudi:", style={'fontWeight': 'bold'}),
            html.Div([
                dcc.Input(id='input', type='text', placeholder='Tu texto aquí...', style={'width': '13vw'}),
                html.Button("🔍", id='btn', n_clicks=0, style={'marginLeft': '5px'}),
                html.Div(id='dropdown-container', children=[], style = {}),
                ], style={'position': 'relative', 'marginLeft': '5px'}),
            c_lay.obtain_search_button(PAGE_NUM),
            html.Div([
                html.Pre(id=f"graph-summary_{PAGE_NUM}", style=c_lay.graph_summary_style),
                html.Div(id=f"leyenda{PAGE_NUM}")
            ],
            style={
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '10px'  # espacio entre el resumen y la leyenda
            }),
            c_lay.obtain_info_box_component(PAGE_NUM),
            dcc.Store(id=f'graph_summary_store_1_{PAGE_NUM}', data=None),
            dcc.Store(id=f'graph_summary_store_2_{PAGE_NUM}', data=None),
            dcc.Store(id='dropdown_data_storing-show', data=[]),  
            dcc.Store(id='dropdown_data_storing-hide', data=[]),
        ],
        style=c_lay.left_column_style),

        # Columna derecha: Grafo centrado
        html.Div([
            c_lay.graph_layout_selector,
            html.Div(id=f"graph_component{PAGE_NUM}"),
            html.Div(id="slider-component", style={'width': '50%', 
                            'margin': '10px auto',               
                            'textAlign': 'center',
                            'marginTop': '5px'})
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
    Output(f"graph_component{PAGE_NUM}", 'children'),
    Output(f'graph_summary_store_1_{PAGE_NUM}', "data"),
    Output("slider-component", "children"),
    Input(f'search-button_{PAGE_NUM}', 'n_clicks'),
    State('input', 'value'),
    prevent_initial_call=True
)
def mostrar_graf(n_clicks, valor):
    global nodes_list, edges_list, nodes_leyenda
    
    if n_clicks == 0:
        raise PreventUpdate
        
    if not valor:
        return dash.no_update  # no hacer nada si los inputs están vacíos

    nodes_list, edges_list = consulta(valor)
    elements_list = nodes_list + edges_list
    
    nodes_leyenda = nodes_list
    
    
    if len(elements_list) == 0:
        return None, None, None
        
    children = c_lay.obtain_graph_component(PAGE_NUM, elements_list, stylesheet.stylesheet)
    
    minimum_year, maximum_year = queries.obtain_minimum_and_maximum_year(nodes_list)    
    slider = c_lay.obtain_range_slider(minimum_year, maximum_year)
    
    graph_summary_store_1 = [len(nodes_list), len(edges_list)]
                    
    return children, graph_summary_store_1, slider

  

@callback(
    Output(f'info-box{PAGE_NUM}', 'children'),
    Input(f'cytoscape-update-layout_{PAGE_NUM}', 'selectedNodeData')
)
def display_node_data(selected_node):
    return c_lay.selected_node_general_function(selected_node)


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


@callback(
    Output(f'cytoscape-update-layout_{PAGE_NUM}', 'elements'),
    Output(f'graph_summary_store_2_{PAGE_NUM}', "data"),
    Input('slider', 'value'),
    prevent_initial_call=True,
)
def update_graph_elements(selected_year_range):    
    global nodes_leyenda
    start_year, end_year = selected_year_range

    filtered_nodes = [
        n for n in nodes_list if (
            'any' not in n['data'] or
            (start_year <= int(n['data']['any']) <= end_year)
        )
    ]

    # Obtener IDs válidos
    valid_node_ids = set(n['data']['id'] for n in filtered_nodes)

    # Filtrar aristas cuyos source y target están en los nodos válidos
    filtered_edges = [
        e for e in edges_list
        if e['data']['source'] in valid_node_ids and e['data']['target'] in valid_node_ids
    ]
    
    graph_summary_store_2 = [len(filtered_nodes), len(filtered_edges)]
    
    nodes_leyenda = filtered_nodes
    print(len(nodes_leyenda))

    return filtered_nodes + filtered_edges, graph_summary_store_2



@callback(
    Output('dropdown_data_storing-show', 'data'), 
    Input('btn', 'n_clicks'),
    State('input', 'value'),
    State('dropdown_data_storing-show', 'data'),  
    prevent_initial_call=True
)
def mostrar_opciones(n_clicks, value_input, dropdown_data_storing):
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
    
    records = queries.text_search(driver, "Camp_Estudi", value_input, limit=10)
        
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
            id={'type': "dropdown-option", 'index': 'dropdown-options'},
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
    Output('input', 'value'),
    Output('dropdown_data_storing-hide', 'data'), 
    Input({'type': 'dropdown-option', 'index': ALL}, 'n_clicks'),
    State({'type': 'dropdown-option', 'index': ALL}, 'children'),
    State('dropdown_data_storing-hide', 'data'),  
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
    Output('dropdown-container', 'children'),
    Output('dropdown-container', 'style'),
    Input('dropdown_data_storing-show', 'data'),  
    Input('dropdown_data_storing-hide', 'data'),
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
    Output(f"graph_component{PAGE_NUM}", 'children', allow_duplicate=True),
    Output(f"leyenda{PAGE_NUM}", "children"),
    Input(f"graph_component{PAGE_NUM}", 'children'),
    Input(f'cytoscape-update-layout_{PAGE_NUM}', 'elements'),
    prevent_initial_call=True
)
def update_graph_stylesheet(children, elements):      
    print("hello update")
    global nodes_leyenda
    print(len(nodes_leyenda))

    
    if not children:
        raise PreventUpdate()
    
    dynamic_style, leyenda = c_lay.obtain_dynamic_styles("etiqueta", nodes_leyenda)
    leyenda = c_lay.generate_legend_component(leyenda)
        
    children["props"]["stylesheet"] += dynamic_style
    
    return children, leyenda
