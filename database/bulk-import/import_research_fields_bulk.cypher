//Import Camp Estudi BIG DATA
:auto LOAD CSV WITH HEADERS FROM 'file:///fieldOfStudy.csv' AS row
CALL {
    WITH row
    MERGE (a:Camp_Estudi {id: row.fieldOfStudy})
} IN TRANSACTIONS OF 10000 ROWS;