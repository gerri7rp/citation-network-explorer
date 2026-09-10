//Import articles-articles
LOAD CSV WITH HEADERS FROM 'file:///articles_articles.csv' AS row
WITH row
MATCH (a1:Article {id: row.article_citant})
MATCH (a2:Article {id: row.article_citat})
MERGE (a1)-[r:CITA_A]->(a2)
RETURN count(r);