//Import Article-Camp estudi BIG DATA
:auto LOAD CSV WITH HEADERS FROM 'file:///articles_fieldOfStudy.csv' AS row
CALL {
    WITH row
    MATCH (a:Article {id: row.id})
    MATCH (c:Camp_Estudi {id: row.fieldOfStudy})
    MERGE (a)-[r:TRACTA_DE]->(c)
    SET r.pes = row.weightOfFieldOfStudy
} IN TRANSACTIONS OF 10000 ROWS;