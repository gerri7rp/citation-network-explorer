# -*- coding: utf-8 -*-
"""
Created on Sun May 18 13:44:02 2025

@author: Gerard
"""


from dash import html, dcc
import dash_cytoscape as cyto
from collections import Counter




def obtain_summary_text(num_nodes, num_edges, graph_type):
    if num_nodes <= 1:
        densitat = 0
    else:
        if graph_type == "Autors": #No dirigit
            densitat = round((2 * num_edges) / (num_nodes * (num_nodes - 1)), 3)
            
        elif graph_type == "Articles": #Dirigit
            densitat = round(num_edges / (num_nodes * (num_nodes - 1)), 3)

    return html.Div([
        html.H4("Resum del graf"),
        html.Div(f"Nodes: {num_nodes}"),
        html.Div(f"Arestes: {num_edges}"),
        html.Div(f"Densitat: {densitat}")
    ])


def generate_legend_component(legend_info, title="LLEGENDA"):
    legend_div = html.Div([
        html.Div(title, id="legend-toggle", style={
            "cursor": "pointer",
            "marginBottom": "10px",
            "textDecoration": "underline"
        }),

        html.Div([
            html.Ul([
                html.Li([
                    html.Span(style={
                        "display": "inline-block",
                        "width": "15px",
                        "height": "15px",
                        "backgroundColor": item["color"],
                        "marginRight": "10px",
                        "borderRadius": "3px",
                        "verticalAlign": "middle"
                    }),
                    f'{item["value"]} ({item["count"]})'
                ],
                style={"marginBottom": "5px"})
                for item in legend_info
            ], style={"listStyleType": "none", "paddingLeft": "0"})
        ], id="legend-content")
    ])

    return legend_div


def obtain_dynamic_styles(color_attribute, nodes):
    if color_attribute == "etiqueta":
        # Colores fijos para etiquetas concretas
        fixed_colors = {
            "Article": "skyblue",
            "Autor": "orange",
            "Camp_Estudi": "red"
        }
        
        # Filtrar nodos que tengan etiqueta válida y estén en fixed_colors
        values = [node['data'].get(color_attribute) for node in nodes if node['data'].get(color_attribute) in fixed_colors]
        
        # Contar ocurrencias
        value_counts = Counter(values)
        
        dynamic_style = [
            {
                'selector': f'.{val}',  # Asumiendo que la clase de los nodos es la etiqueta
                'style': {
                    'background-color': fixed_colors[val]
                }
            }
            for val in fixed_colors if val in value_counts
        ]
        
        legend = [
            {
                'value': val,
                'color': fixed_colors[val],
                'count': value_counts[val]
            } for val in fixed_colors if val in value_counts
        ]
        
        return dynamic_style, legend
    
    # Código original para otros atributos
    values = [node['data'].get(color_attribute) for node in nodes if node['data'].get(color_attribute) is not None]

    value_counts = Counter(values)

    sorted_values = [val for val, _ in value_counts.most_common()]
    n = len(sorted_values)

    color_map = {}
    for i, val in enumerate(sorted_values):
        hue = int((360 * i) / max(n, 1))
        color_map[val] = f"hsl({hue}, 65%, 55%)"

    dynamic_style = [
        {
            'selector': f'[ {color_attribute} = "{val}" ]',
            'style': {
                'background-color': color_map[val]
            }
        } for val in sorted_values
    ]

    legend = [
        {
            'value': val,
            'color': color_map[val],
            'count': value_counts[val]
        } for val in sorted_values
    ]

    return dynamic_style, legend



go_back_to_menu_button =  dcc.Link(
     html.Button("⬅", style={"background-color": "#f0f0f0"}),
     href="/"
)

graph_summary_style = {
    'textAlign': 'left',
    'fontSize': '12px',
    'overflowY': 'auto',
    'marginTop': 'auto'}


options_dropdown_style = {
    'position': 'absolute',
    'backgroundColor': 'white',
    'border': '1px solid #ccc',
    'zIndex': 1000,
    'width': '13vw',
    'maxHeight': '150px',
    'overflowY': 'auto',
    'marginTop': '2px',
    'display': 'block',
    'boxShadow': '0px 2px 6px rgba(0,0,0,0.2)',
}


def obtain_info_box_component(page_num: str):
    info_box_component = html.Div(
        id = f'info-box{page_num}',
        style={
            'height': '120px',
            'marginTop': 'auto',  # lo empuja hacia abajo
            'backgroundColor': 'rgba(255, 255, 255, 0.95)',
            'padding': '10px 20px',
            'border': '1px solid #ccc',
            'borderRadius': '5px',
            'boxShadow': '2px 2px 10px rgba(0,0,0,0.1)',
            'overflowY': 'auto',
            'fontSize': '14px',
            'whiteSpace': 'normal'
        }
    )
    return info_box_component

def obtain_range_slider(minimum_year, maximum_year):
    range_slider = dcc.RangeSlider(
        id='slider',
        min=minimum_year,
        max=maximum_year,
        step=1,
        value=[minimum_year, maximum_year],
        marks={i: str(i) for i in range(minimum_year, maximum_year + 1, 3)},
        tooltip={"placement": "bottom", "always_visible": True}
        )
    
    return range_slider


screen_style = {
    'display': 'flex',
    'flexDirection': 'row',
    'overflow': 'hidden',   # Evita cualquier scroll vertical u horizontal
    'margin': '0',
    'padding': '0'
}


left_column_style = {
    'display': 'flex',
    'flexDirection': 'column',
    'justifyContent': 'space-between',  # o flex-start si no usas margin auto
    'height': '100vh',
    'width': '22vw',
    'padding': '20px',
    'boxSizing': 'border-box',
    'borderRight': '2px solid #ccc',
    'backgroundColor': '#f9f9f9',
    'overflowY': 'auto'
}



right_column_style = {
    'width': '80vw',
    'padding': '20px',
    'display': 'flex',
    'flexDirection': 'column',    # importante para apilar verticalmente
    'alignItems': 'center',       # centra horizontalmente
    'boxSizing': 'border-box',
    'backgroundColor': '#fdfdfd'
}


# right_column_style={'display': 'flex', 'justify-content': 'center', 'position': 'relative'}

flechas_component = html.Div([html.Button(
        html.I(className="fa-solid fa-chevron-left"),  # Ícono de flecha izquierda
        id='btn-prev', 
        n_clicks=0, 
        style={'font-size': '24px', 'border' : "none", 'color': 'grey', 'padding': '10px', 'background-color': 'transparent'}
    ),
    html.Button(
        html.I(className="fa-solid fa-chevron-right"),  # Ícono de flecha derecha
        id='btn-next', 
        n_clicks=0, 
        style={'font-size': '24px', 'border': 'none', 'color': 'grey', 'padding': '10px', 'background-color': 'transparent'}
    )
    ], 
    style={
        'display': 'flex',
        'justify-content': 'space-between', 
        'position': 'absolute',  
        'top': '50%', 
        'width': '77%',
        'transform': 'translateY(-50%)',
        "backgroundColor" : "transparent",
    })


flechas_component = html.Div(
    flechas_component,
    style={
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'margin': '20px auto',
    }
)


def obtain_community_index_label(graphs_list):
    community_index_label = html.Div(id='community-index-label', 
        children=f"Comunitat 1 de {len(graphs_list)}",
        style={'textAlign': 'center', 'marginTop': '10px', 'fontWeight': 'bold'})
    
    return community_index_label


def obtain_graph_component(page_num: str, elements_list: list, stylesheet: list):
    graph_component = cyto.Cytoscape(
            id=f'cytoscape-update-layout_{page_num}',
            style={'width': '70vw', 'height': '80vh', 'zIndex' : '100'},# 'margin': 'auto'},
            zoom=0.2, wheelSensitivity=0.2,
            layout={'name': 'concentric', 'animate': True},
            elements=elements_list, stylesheet=stylesheet
    )
    
    return graph_component


graph_layout_selector = dcc.Dropdown(
        id='dropdown-update-layout',
        value='cose',
        clearable=False,
        options=[
            {'label': name.capitalize(), 'value': name}
            for name in ['grid', 'random', 'circle', 'cose', 'concentric']
        ],
        style={'width': '8vw', 'margin': '0 auto', "textAlign" : "left", 'marginBottom': '20px'}
)


def obtain_search_button(page_num: str):
    search_button = html.Button("Cercar", id=f'search-button_{page_num}', n_clicks=0, style={'width': '10vw', 'marginTop': '10px'})
    return search_button



def selected_node_general_function(selected_node):
    if not selected_node:
        return html.Div("Node seleccionat:", style={
            'textDecoration': 'underline', 'fontWeight': 'normal',
            'fontSize': '14px', 'marginBottom': '10px'
        })
    
    node = selected_node[0]
    info = [html.Div("Node seleccionat:", style={
        'textDecoration': 'underline', 'fontWeight': 'normal',
        'fontSize': '14px', 'marginBottom': '10px'
    })]
    
    
    # Añadir centralidad si existe
    if 'centrality' in node:
        info.append(
            html.Div([
                html.Strong("Centrality: "),
                f"{node['centrality']:.2f}"
            ])
        )   
    
    tipus = node.get("etiqueta")
    
    if tipus == "Article":
        info += [
            html.Div([
                html.Strong("Títol: "),
                node.get('nom', '')
            ]),
            html.Div([
                html.Strong("Any: "),
                node.get('any', '')
            ]),
            html.Div([
                html.Strong("URL: "),
                html.A(node.get('url', ''), href=node.get('url', ''), target="_blank")
            ])
        ]
    
    elif tipus == "Autor":
        info += [
            html.Div([
                html.Strong("Nom: "),
                node.get('nom', '')
            ]),
            html.Div([
                html.Strong("Organització: "),
                node.get('organitzacio', '')
            ])
        ]
        
    else:
        info.append(
            html.Div([
                html.Strong("Nom: "),
                node['id']
            ])
        )
        

    
    return info