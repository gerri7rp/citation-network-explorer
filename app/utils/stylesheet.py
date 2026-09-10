# -*- coding: utf-8 -*-
"""
Created on Sun May  4 20:27:44 2025

@author: Gerard
# """




stylesheet_tipus_node = [
    {
        'selector': '.Article',
        'style': {
            'background-color': 'skyblue'
        }
    },
    {
        'selector': '.Autor',
        'style': {
            'background-color': 'orange'
        }
    },
    {
        'selector': '.Camp_Estudi',
        'style': {
            'background-color': 'red'
        }
    }
]



stylesheet = [
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'background-color': '#0074D9',
            'color': 'black',
            'font-size': '6px',
            'text-valign': 'center',
            'text-halign': 'center',
            'width': 'data(size)',#'20px',    
            'height': 'data(size)'
        }
    },
    {
        'selector': '.Article',
        'style': {
            'background-color': 'skyblue'
        }
    },
    {
        'selector': '.Autor',
        'style': {
            'background-color': 'orange'
        }
    },
    {
        'selector': '.Camp_Estudi',
        'style': {
            'background-color': 'red'
        }
    },
    {
        'selector': '[positionInPath = "Start"]',
        'style': {
            'color': 'blue'
        }
    },
    {
        'selector': '[positionInPath = "End"]',
        'style': {
            'color': 'green'
        }
    },
    {
     'selector': 'node:selected',
        'style': {
            'border-color': 'black',
            'border-width': 1,
            'border-opacity': 1
        }
    },
    {
    'selector': 'edge',
    'style': {
        'font-size': '10px',
        'width': 0.8,
        'line-color': '#ccc',
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle',
        'target-arrow-color': '#ccc',
        'arrow-scale': 0.5
        }
    },
    {
        'selector': 'edge[type = "COAUTORIA"]',
        'style': {
            'target-arrow-shape': 'none',
            "label" : "data(pes)",
            'font-size': '6.5px',
            'text-rotation': 'autorotate',
            'text-margin-y': '-5px',
            'color': '#333'
        }
    },
    {
        'selector': 'edge[type = "TRACTA_DE"]',
        'style': {
            'target-arrow-shape': 'none',
            "label" : "data(pes)",
            'font-size': '6.5px',
            'text-rotation': 'autorotate',
            'text-margin-y': '-5px',
            'color': '#333'
        }
    }
]

