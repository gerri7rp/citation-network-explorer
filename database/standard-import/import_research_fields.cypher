//Import Camp_Estudi
LOAD CSV WITH HEADERS FROM 'file:///fieldOfStudy.csv' AS row
WITH row
MERGE (a:Camp_Estudi {id: row.Name})
RETURN count(a);