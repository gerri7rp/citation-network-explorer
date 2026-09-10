# -*- coding: utf-8 -*-
"""
Created on Sat May 17 18:33:46 2025

@author: Gerard
"""


def truncate_label(label, max_len=14):
    return label[:max_len] + "…" if len(label) > max_len else label


def prepare_nodes(nodes, sizes, isShortestPath=False, centralities = None):
    node_list = []
    
    for i, node in enumerate(nodes):
        if node:
            node_data = {}
            
            etiqueta = next(iter(node.labels))
            id_ = node.get("id")
        
            if etiqueta == "Article":
                label = truncate_label(node.get("titol"))        
                nom = (node.get("titol"))        
                node_data["any"] = node.get("any")
                url = node.get("url")
                if url: 
                    node_data["url"] = url.split(",")[0]
        
            elif etiqueta == "Autor":
                label = truncate_label(node.get("nom"))      
                nom = (node.get("nom"))        
                node_data["organitzacio"] = node.get("organitzacio", "Desconeguda")
        
            else: # Camp Estudi
                label = id_
                nom = label
                
            if centralities:
                node_data["centrality"] = centralities[i]
                
            node_data["size"] = sizes[i]
            node_data["id"]       = id_
            node_data["label"]    = label
            node_data["etiqueta"] = etiqueta
            node_data["nom"]      = nom
            
            if isShortestPath:
                node_data["positionInPath"] = "Middle"
        
            node_list.append({"data" : node_data, "classes" : etiqueta})
        
    return node_list
    
    
def prepare_edges(edges):   
    edge_list = []
    for edge in edges:
        if edge != None:
            print(edge)
            source = edge.start_node.get("id")
            target = edge.end_node.get("id")
            tipus_rel = edge.type
            weight = edge.get("pes")
            
            if weight:
                weight = round(float(weight), 2)
            
            edge_list.append({"data" : {"source" : source, "target" : target, "type" : tipus_rel, "label" : tipus_rel, "pes" : weight}})
            
    return edge_list


def prepare_nodes_and_edges(records, isShortestPath=False, centralities = None):
    nodes_list = []
    edges_list = []
    
    print("keys:",records[0].keys())
    
    if "Camp_Estudi" in records[0].keys():
        nodes_list += prepare_nodes([records[0]["Camp_Estudi"]], [20] * len([records[0]["Camp_Estudi"]]), isShortestPath, centralities)
    
    for record in records:
        if "p" in record.keys():
            path = record["p"]
            
            nodes_list += prepare_nodes(path.nodes, [20] * len(path.nodes), isShortestPath, centralities)
            edges_list += prepare_edges(path.relationships)
            
        elif "Article" in record.keys():  
            nodes_list += prepare_nodes([record["Article"]], [20] * len([record["Article"]]), isShortestPath, centralities)
            edges_list += prepare_edges([record["Relacio"]])
            
    return nodes_list, edges_list