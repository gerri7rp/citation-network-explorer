//Import autors
:auto LOAD CSV WITH HEADERS FROM 'file:///autors.csv' AS row
WITH row
MERGE (a:Autor {id: row.id})
SET a.nom = row.name, a.organitzacio = row.organization
RETURN count(a);