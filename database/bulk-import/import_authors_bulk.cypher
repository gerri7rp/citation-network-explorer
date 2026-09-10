//Import autors BIG DATA
:auto LOAD CSV WITH HEADERS FROM 'file:///autors.csv' AS row
CALL {
    WITH row
    MERGE (a:Autor {id: row.authorsId})
    SET a.nom = row.name, a.organitzacio = row.organization
} IN TRANSACTIONS OF 10000 ROWS;