//Import articles-autors
LOAD CSV WITH HEADERS FROM 'file:///articles_autors.csv' AS row
WITH row
MATCH (ar:Article {id: row.id_article})
MATCH (au:Autor {id: row.id_autor})
MERGE (au)-[rel:ESCRIU]->(ar)
RETURN count(rel);