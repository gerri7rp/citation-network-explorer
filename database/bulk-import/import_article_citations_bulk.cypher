//Import Article-Article BIG DATA
:auto LOAD CSV WITH HEADERS FROM 'file:///articles_articles.csv' AS row
CALL {
    WITH row
    MATCH (a1:Article {id: row.article_citant})
    MATCH (a2:Article {id: row.article_citat})
    MERGE (a1)-[r:CITA_A]->(a2)
} IN TRANSACTIONS OF 10000 ROWS;