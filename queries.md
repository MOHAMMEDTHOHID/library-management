# Neo4j Browser queries
// Members and the books they read
MATCH (m:Member)-[:READ]->(b:Book) RETURN m, b;
// Book -> author and genre
MATCH (b:Book)-[:WRITTEN_BY]->(a:Author), (b)-[:IN_GENRE]->(g:Genre) RETURN b, a, g;
// Collaborative recommendation for a member
MATCH (m:Member {name:'Asha'})-[:READ]->(:Book)<-[:READ]-(o:Member)-[:READ]->(rec:Book)
WHERE NOT (m)-[:READ]->(rec)
RETURN rec.title AS Recommended, count(DISTINCT o) AS SimilarReaders ORDER BY SimilarReaders DESC;
// Same-genre recommendation
MATCH (m:Member {name:'Asha'})-[:READ]->(:Book)-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(rec:Book)
WHERE NOT (m)-[:READ]->(rec) RETURN rec.title, collect(DISTINCT g.name) AS Genres;

# MongoDB shell queries
db.books.insertOne({title:"Clean Code", author:"Robert Martin", genre:"Programming", year:2008, copies:3})
db.books.find({genre:"Programming"})
db.books.updateOne({title:"Clean Code"}, {$set:{copies:5}})
db.books.deleteOne({title:"Clean Code"})
db.loans.find({status:"issued"})
db.loans.aggregate([{$group:{_id:"$book_id", times:{$sum:1}}},{$sort:{times:-1}}])
