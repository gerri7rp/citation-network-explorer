// Importar relaciones de coautoría basadas en artículos compartidos
:auto MATCH (au1:Autor)-[:ESCRIU]->(a:Article)<-[:ESCRIU]-(au2:Autor)
WHERE id(au1) < id(au2)
WITH au1, au2, count(DISTINCT a) AS pes
CALL {
    WITH au1, au2, pes
    MERGE (au1)-[r:COAUTORIA]->(au2)
    SET r.pes = pes
} IN TRANSACTIONS OF 10000 ROWS;
