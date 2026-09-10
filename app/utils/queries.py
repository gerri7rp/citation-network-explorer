# -*- coding: utf-8 -*-
"""
Created on Sun May  4 20:18:34 2025

@author: Gerard
"""
    
final_consultas_communities = """
        ORDER BY mida DESC
        LIMIT $num_communities
        
        // Obtener nodos
        UNWIND nodes AS id_n
        MATCH (n)
        WHERE id(n) = id_n
        
        WITH nodes, collect(n) AS nodos_comunitat
        
        // Obtener relaciones internas entre esos nodos
        UNWIND nodes AS id1
        UNWIND nodes AS id2
        MATCH (n1)-[r]-(n2)
        WHERE id(n1) = id1 AND id(n2) = id2 AND id(n1) < id(n2)  // evita duplicados
        WITH nodos_comunitat, collect(DISTINCT r) AS rels_comunitat
        
        RETURN nodos_comunitat AS nodes, rels_comunitat AS edges
        """
        
        
final_consultas_centralities = """      
        YIELD nodeId, score
        WITH nodeId, score, gds.util.asNode(nodeId) AS node
        WITH collect(node) AS nodes, collect(score) AS scores
        
        UNWIND nodes AS n1
        UNWIND nodes AS n2
        OPTIONAL MATCH (n1)-[r]-(n2)
        WHERE id(n1) < id(n2)  // evita duplicar relaciones
        WITH DISTINCT r, nodes, scores
        WHERE r IS NOT NULL
        
        RETURN nodes, collect(DISTINCT r) AS edges, scores
        """


def shortest_path_autors(driver, id_autor_1, id_autor_2):
    consulta = """
        MATCH p = SHORTEST 1 (a1:Autor)-[:COAUTORIA]-+(a2:Autor)
        WHERE a1.id = $id_autor_1 AND a2.id = $id_autor_2
        RETURN p
        """

    records, summary, keys = driver.execute_query(consulta, 
                                              id_autor_1 = id_autor_1,
                                              id_autor_2 = id_autor_2)
    return records



def shortest_path_articles(driver, id_article_1, id_article_2):
    consulta = """
        MATCH p=SHORTEST 1 (a1:Article)-[:CITA_A]-+(a2:Article)
        WHERE a1.id = $id_article_1 AND a2.id = $id_article_2
        RETURN p
        """

    records, summary, keys = driver.execute_query(consulta, 
                                                  id_article_1 = id_article_1, 
                                                  id_article_2 = id_article_2)
    return records



def obtenir_node_i_veins(driver, nom, tipus_node, tipus_veins):
    if tipus_node == "Article":
        consulta = f"""
            MATCH (n:{tipus_node})
            WHERE n.titol = $nom
            OPTIONAL MATCH (n)-[r]-(v:{tipus_veins})
            RETURN n as Camp_Estudi, r as Relacio, v as Article
            """
    
    elif tipus_node == "Autor":
        consulta = f"""
            MATCH (n:{tipus_node})
            WHERE n.nom = $nom
            OPTIONAL MATCH (n)-[r]-(v:{tipus_veins})
            RETURN n as Camp_Estudi, r as Relacio, v as Article
            """
            
    elif tipus_node == "Camp_Estudi":
        consulta = f"""
            MATCH (n:{tipus_node})
            WHERE n.id = $nom
            OPTIONAL MATCH (n)-[r]-(v:{tipus_veins})
            RETURN n as Camp_Estudi, r as Relacio, v as Article
            """

    records, summary, keys = driver.execute_query(consulta, 
                                                  nom = nom)
    return records


def evolucio_camp_estudi(driver, nom_camp_estudi):
    consulta = """
        MATCH (a:Article)-[r:TRACTA_DE]->(c:Camp_Estudi)
        WHERE c.id = $nom_camp_estudi
        RETURN c as Camp_Estudi, r as Relacio, a as Article
        """
        
    records, summary, keys = driver.execute_query(consulta, 
                                                  nom_camp_estudi = nom_camp_estudi)
    return records



def obtain_minimum_and_maximum_year(nodes):
    any_ = int(nodes[1]["data"]["any"])
    
    minimum_year = any_
    maximum_year = any_
    
    for node in nodes[2:]: # El 1o es camp-estudi y el 2o se hace arriba
        any_ = int(node["data"]["any"])
        
        if any_ > maximum_year:
            maximum_year = any_
            
        if any_ < minimum_year:
            minimum_year = any_
            
    return minimum_year, maximum_year



def check_graph_exists(driver, graph_name):
    consulta = """
        CALL gds.graph.exists($graph_name) YIELD exists
        RETURN exists
        """
    records, summary, keys = driver.execute_query(consulta, graph_name=graph_name)

    return records[0]["exists"]



def load_graph_to_memory(driver, graph_name):
    is_exists = check_graph_exists(driver, graph_name)        
    
    if not is_exists:
        if graph_name == "graph-autors":
            consulta = """
                CALL gds.graph.project($graph_name, ['Autor'], ['COAUTORIA'])
                """
                
        elif graph_name == "graph-articles":
            consulta = """
                CALL gds.graph.project($graph_name, ['Article'], ['CITA_A'])
                """
                
        records, summary, keys = driver.execute_query(consulta, graph_name=graph_name)
        
        
def execute_community_algorithm(driver, graph_name, algorithm, num_communities):
    load_graph_to_memory(driver, graph_name)
        
    if algorithm == "WCC":
        consulta = """
            CALL gds.wcc.stream($graph_name)
            YIELD componentId, nodeId
            WITH componentId, collect(nodeId) AS nodes, size(collect(nodeId)) AS mida
            """ 
        
    elif algorithm == "Label Prop":
        consulta = """
            CALL gds.labelPropagation.stream($graph_name)
            YIELD communityId, nodeId
            WITH communityId, collect(nodeId) AS nodes, size(collect(nodeId)) AS mida
            """
            
    elif algorithm == "Louvain Mod":
        consulta = """
            CALL gds.louvain.stream($graph_name)
            YIELD communityId, nodeId
            WITH communityId, collect(nodeId) as nodes, size(collect(nodeId)) as mida
            """
            
    else:
        print("ALgoritmo no existente")
        return
        
        
    consulta += final_consultas_communities
        
    records, summary, keys = driver.execute_query(consulta, graph_name=graph_name, num_communities=num_communities)
    return records


def execute_centrality_algorithm(driver, graph_name, algorithm):
    load_graph_to_memory(driver, graph_name)

    if algorithm == "Page Rank":
        consulta = "CALL gds.pageRank.stream($graph_name)"
        
    elif algorithm == "Betweenness Centrality":
        consulta = "CALL gds.betweenness.stream($graph_name)"
        
    else:
        print("ALgoritmo no existente")
        return
    
    consulta += final_consultas_centralities
        
    records, summary, keys = driver.execute_query(consulta, graph_name=graph_name)
    return records

    
    
def text_search(driver, node_type, text, limit):
    
    if node_type == "Autor":
        consulta = """
            MATCH (a:Autor)
            WHERE toLower(a.nom) CONTAINS toLower($text)
            LIMIT $limit
            RETURN a as nodes
            """
    elif node_type == "Article":
        consulta = """
            MATCH (a:Article)
            WHERE toLower(a.titol) CONTAINS toLower($text)
            LIMIT $limit
            RETURN a as nodes
            """
            
    elif node_type == "Camp_Estudi":
        consulta = """
            MATCH (a:Camp_Estudi)
            WHERE toLower(a.id) CONTAINS toLower($text)
            LIMIT $limit
            RETURN a as nodes
            """
            
    else:
        print("No correct graph type selected")
        return []
        
    records, summary, keys = driver.execute_query(consulta, text=text, limit=limit)
    return records
    

        
        
        

# def obtain_subgraph_autors(driver, limit=1000):
#     consulta = """
#         CALL {
#           MATCH (n:Autor)
#           RETURN DISTINCT n AS node
#           UNION
#           MATCH (:Autor)-[:COAUTORIA]->(m:Autor)
#           RETURN DISTINCT m AS node
#         }
#         WITH collect(DISTINCT node) AS nodes
#         MATCH (a:Autor)-[r:COAUTORIA]->(b:Autor)
#         RETURN nodes, collect(DISTINCT r) AS edges;
#         """
#     records, summary, keys = driver.execute_query(consulta)
#     return records    


# def obtain_subgraph_articles(driver, limit=1000):
#     consulta = """
#         CALL {
#           MATCH (n:Article)
#           RETURN DISTINCT n AS node
#           UNION
#           MATCH (:Article)-[:CITA_A]->(m:Article)
#           RETURN DISTINCT m AS node
#         }
#         WITH collect(DISTINCT node) AS nodes
#         MATCH (a:Article)-[r:CITA_A]->(b:Article)
#         RETURN nodes, collect(DISTINCT r) AS edges;
#         """
        
#     records, summary, keys = driver.execute_query(consulta)#, limit=limit)
#     return records    


# def obtain_complete_graph(driver, limit=1000):
#     consulta = """
#         MATCH (n)
#         OPTIONAL MATCH (n)-[r]->(m)
#         LIMIT $limit
#         RETURN collect(DISTINCT n) + collect(DISTINCT m) as nodes, collect(DISTINCT r) as edges        
#         """

#     records, summary, keys = driver.execute_query(consulta, limit=limit)
#     return records