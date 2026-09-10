//Import articles BIG DATA
:auto LOAD CSV WITH HEADERS FROM 'file:///articles.csv' AS row
CALL {
    WITH row
    MERGE (a:Article {id: row.id})
    SET a.titol = row.title, a.any = row.year, a.url = row.url
} IN TRANSACTIONS OF 10000 ROWS;