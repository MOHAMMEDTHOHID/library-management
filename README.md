# Library Management and Book Recommendation System (Flask + MongoDB + Neo4j)
Setup: pip install -r requirements.txt
Set env vars (or edit defaults in app.py): MONGO_URI, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
Run: python app.py  ->  http://127.0.0.1:5000
Note: not tested against your own database accounts; verify both connections first.

| Data | MongoDB | Neo4j |
|---|---|---|
| Books, members, loans (with copies, dates, status) | yes (system of record) | only id/title/name |
| Member-READ->Book, Book-WRITTEN_BY->Author, Book-IN_GENRE->Genre | no | yes |

Why two databases: MongoDB suits flexible, document-style records and transactional-style updates (copies, loan status). Neo4j suits relationship traversal, so "readers like you also read" is one short Cypher pattern instead of several joins/lookups.
Demo order: add books -> add members -> issue books (creates READ links) -> Recommend -> show Neo4j Browser graph -> return/delete.
