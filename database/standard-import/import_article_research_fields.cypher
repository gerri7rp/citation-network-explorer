//import articles-camp_estudi
LOAD CSV WITH HEADERS FROM 'file:///articles_fieldOfStudy.csv' AS row
WITH row
MATCH (a:Article {id: row.id_article})
MATCH (c:Camp_Estudi {id: row.fieldOfStudy})
MERGE (a)-[r:TRACTA_DE]->(c)
SET r.pes = row.weightOfFieldOfStudy
RETURN count(r);