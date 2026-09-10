//Import articles
//ARTICLES
LOAD CSV WITH HEADERS FROM 'file:///articles.csv' AS row
WITH row
MERGE (a:Article {id: row.id})
SET a.titol = row.title, a.any = row.year
RETURN count(a);