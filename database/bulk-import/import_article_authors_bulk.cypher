//Import Articles - Autors BIG DATA
:auto LOAD CSV WITH HEADERS FROM 'file:///articles_autors.csv' AS row
CALL {
    WITH row
    MATCH (ar:Article {id: row.id})
    MATCH (au:Autor {id: row.authorsId})
    MERGE (au)-[rel:ESCRIU]->(ar)
} IN TRANSACTIONS OF 10000 ROWS;