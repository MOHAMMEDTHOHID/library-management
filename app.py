import os, datetime, certifi
from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from bson import ObjectId
from neo4j import GraphDatabase

app = Flask(__name__)

# MongoDB Atlas connection with certifi SSL bundle
db = MongoClient(
    os.getenv(
        "MONGO_URI",
        "mongodb+srv://thohidmohammed2_db_user:S%40thohid@cluster0.dxgdvub.mongodb.net/?retryWrites=true&w=majority"
    ),
    tlsCAFile=certifi.where()
)["library"]

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "neo4j+s://5a344e0c.databases.neo4j.io"),
    auth=(
        os.getenv("NEO4J_USER", "5a344e0c"),
        os.getenv("NEO4J_PASSWORD", "4h5PTWOpCktuUTBhnmyP0UKw_tEd5UrSuZCY9Eu8Obk")
    )
)

def cypher(q, **p):
    try:
        with driver.session() as s:
            return [r.data() for r in s.run(q, **p)]
    except Exception as e:
        print("Neo4j fallback notice:", e)
        return []

def ser(d):
    if not d:
        return {}
    d = dict(d)
    d["_id"] = str(d["_id"])
    d.pop("password", None)
    return d

def oid(x):
    return ObjectId(x)

def sync_book(b):
    cypher("""MERGE (b:Book {id:$id}) SET b.title=$title
              WITH b OPTIONAL MATCH (b)-[r:WRITTEN_BY|IN_GENRE]->() DELETE r
              WITH DISTINCT b
              MERGE (a:Author {name:$author}) MERGE (g:Genre {name:$genre})
              MERGE (b)-[:WRITTEN_BY]->(a) MERGE (b)-[:IN_GENRE]->(g)""",
           id=str(b["_id"]), title=b["title"], author=b["author"], genre=b["genre"])

def seed_initial_data():
    """Seeds Section 11 Folio demo accounts, catalog books, and active loan if empty."""
    if db.members.count_documents({"email": "doc.demo.student@folio.example.com"}) == 0:
        student = {
            "name": "Documentation Demo Student",
            "email": "doc.demo.student@folio.example.com",
            "password": "password123",
            "department": "B.Tech Engineering",
            "studentId": "DOC-DEMO-001",
            "role": "Student"
        }
        student["_id"] = db.members.insert_one(student).inserted_id
        cypher("MERGE (m:Member {id:$id}) SET m.name=$name", id=str(student["_id"]), name=student["name"])
    else:
        student = db.members.find_one({"email": "doc.demo.student@folio.example.com"})

    if db.members.count_documents({"email": "librarian@folio.example.com"}) == 0:
        librarian = {
            "name": "Documentation Demo Librarian",
            "email": "librarian@folio.example.com",
            "password": "password123",
            "department": "Central Library",
            "studentId": "LIB-DEMO-001",
            "role": "Librarian"
        }
        librarian["_id"] = db.members.insert_one(librarian).inserted_id
        cypher("MERGE (m:Member {id:$id}) SET m.name=$name", id=str(librarian["_id"]), name=librarian["name"])

    if db.books.count_documents({}) == 0:
        sample_books = [
            {
                "title": "Advanced Engineering Mathematics",
                "author": "Erwin Kreyszig",
                "genre": "Engineering",
                "publisher": "Wiley",
                "edition": "10th",
                "year": 2021,
                "copies": 1,
                "total_copies": 3,
                "accession": "ACC-002-02",
                "shelf": "Centre Library · BT-MATH-02",
                "description": "Advanced Engineering Mathematics by Erwin Kreyszig, 10th edition, published by Wiley in 2021. Covers Engineering Mathematics, Differential Equations, Linear Algebra for B.Tech and engineering courses."
            },
            {
                "title": "BARC Chemical Engineering: Previous Years' Solved Papers",
                "author": "GKP Editorial Team",
                "genre": "Engineering",
                "publisher": "GKP",
                "edition": "2024",
                "year": 2024,
                "copies": 2,
                "total_copies": 2,
                "accession": "ACC-101-01",
                "shelf": "Centre Library · GATE-CH-01",
                "description": "Solved papers and practice sets for BARC Chemical Engineering competitive examinations."
            },
            {
                "title": "BARC Mechanical Engineering: Previous Years' Solved Papers",
                "author": "GKP Editorial Team",
                "genre": "Engineering",
                "publisher": "GKP",
                "edition": "2024",
                "year": 2024,
                "copies": 2,
                "total_copies": 2,
                "accession": "ACC-102-01",
                "shelf": "Centre Library · GATE-ME-01",
                "description": "Comprehensive solved papers for BARC Mechanical Engineering aspirants."
            },
            {
                "title": "ISRO Scientist/Engineer Computer Science: Previous Years' Solved Papers",
                "author": "GKP Editorial Team",
                "genre": "Computer Science & Engineering",
                "publisher": "GKP",
                "edition": "2024",
                "year": 2024,
                "copies": 2,
                "total_copies": 2,
                "accession": "ACC-103-01",
                "shelf": "Centre Library · CSE-ISRO-01",
                "description": "Previous years' solved papers tailored for ISRO Scientist/Engineer Computer Science exams."
            },
            {
                "title": "Clean Code",
                "author": "Robert Martin",
                "genre": "Computer Science & Engineering",
                "publisher": "Prentice Hall",
                "edition": "1st",
                "year": 2008,
                "copies": 3,
                "total_copies": 3,
                "accession": "ACC-201-01",
                "shelf": "Centre Library · CSE-SW-01",
                "description": "A Handbook of Agile Software Craftsmanship."
            }
        ]
        for b in sample_books:
            b["_id"] = db.books.insert_one(b).inserted_id
            sync_book(b)

        first_book = db.books.find_one({"title": "Advanced Engineering Mathematics"})
        if first_book and student and db.loans.count_documents({}) == 0:
            loan = {
                "member_id": str(student["_id"]),
                "book_id": str(first_book["_id"]),
                "accession": "ACC-002-02",
                "status": "issued",
                "issued": "2026-10-30",
                "due": "Nov 13, 2026"
            }
            db.loans.insert_one(loan)
            cypher("""MATCH (m:Member {id:$m}),(b:Book {id:$b})
                      MERGE (m)-[r:READ]->(b) SET r.last=$d""",
                   m=str(student["_id"]), b=str(first_book["_id"]), d=loan["issued"])

@app.route("/")
def home():
    return render_template("index.html")

# ---------- Authentication (Login & Registration) ----------
@app.post("/api/auth/login")
def login():
    d = request.json or {}
    email = (d.get("email") or "").strip().lower()
    password = d.get("password") or ""
    m = db.members.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})
    if not m or (m.get("password") and m.get("password") != password):
        return jsonify(error="Invalid email or password."), 401
    return jsonify(user=ser(m))

@app.post("/api/auth/register")
def register():
    d = request.json or {}
    email = (d.get("email") or "").strip().lower()
    if not email or not d.get("name"):
        return jsonify(error="Name and email are required."), 400
    if db.members.find_one({"email": email}):
        return jsonify(error="An account with this email already exists."), 409
    count = db.members.count_documents({}) + 1
    m = {
        "name": d["name"].strip(),
        "email": email,
        "password": d.get("password", "password123"),
        "department": d.get("department", "B.Tech CSE"),
        "studentId": d.get("studentId") or f"DOC-DEMO-{count:03d}",
        "role": d.get("role", "Student")
    }
    m["_id"] = db.members.insert_one(m).inserted_id
    cypher("MERGE (m:Member {id:$id}) SET m.name=$name", id=str(m["_id"]), name=m["name"])
    return jsonify(user=ser(m)), 201

# ---------- Books (MongoDB CRUD + Graph Sync) ----------
@app.post("/api/books")
def add_book():
    d = request.json
    copies = int(d.get("copies") or 1)
    b = {
        "title": d["title"],
        "author": d["author"],
        "genre": d["genre"],
        "publisher": d.get("publisher", "Wiley"),
        "edition": d.get("edition", "1st"),
        "year": int(d.get("year") or 2024),
        "copies": copies,
        "total_copies": int(d.get("total_copies") or copies),
        "accession": d.get("accession") or f"ACC-{db.books.count_documents({})+1:03d}-01",
        "shelf": d.get("shelf", "Centre Library · Main Stack"),
        "description": d.get("description", f"{d['title']} by {d['author']}.")
    }
    b["_id"] = db.books.insert_one(b).inserted_id
    sync_book(b)
    return jsonify(ser(b)), 201

@app.get("/api/books")
def list_books():
    q = request.args.get("q", "").strip()
    f = {"$or": [
        {"title": {"$regex": q, "$options": "i"}},
        {"author": {"$regex": q, "$options": "i"}},
        {"genre": {"$regex": q, "$options": "i"}},
        {"accession": {"$regex": q, "$options": "i"}}
    ]} if q else {}
    return jsonify([ser(b) for b in db.books.find(f)])

@app.delete("/api/books/<id>")
def delete_book(id):
    db.books.delete_one({"_id": oid(id)})
    cypher("MATCH (b:Book {id:$id}) DETACH DELETE b", id=id)
    return jsonify(ok=True)

# ---------- Members ----------
@app.get("/api/members")
def list_members():
    return jsonify([ser(m) for m in db.members.find()])

# ---------- Loans (MongoDB) + READ Relationship (Neo4j) ----------
@app.post("/api/issue")
def issue():
    d = request.json
    book = db.books.find_one({"_id": oid(d["book_id"])})
    if not book or book.get("copies", 0) <= 0:
        return jsonify(error="No copies available for checkout"), 400
    db.books.update_one({"_id": oid(d["book_id"])}, {"$inc": {"copies": -1}})
    today = datetime.date.today()
    due_date = (today + datetime.timedelta(days=14)).strftime("%b %d, %Y")
    loan = {
        "member_id": d["member_id"],
        "book_id": d["book_id"],
        "accession": book.get("accession", "ACC-002-02"),
        "status": "issued",
        "issued": today.isoformat(),
        "due": due_date
    }
    loan["_id"] = db.loans.insert_one(loan).inserted_id
    cypher("""MATCH (m:Member {id:$m}),(b:Book {id:$b})
              MERGE (m)-[r:READ]->(b) SET r.last=$d""",
           m=d["member_id"], b=d["book_id"], d=loan["issued"])
    return jsonify(ser(loan)), 201

@app.post("/api/return/<id>")
def return_book(id):
    loan = db.loans.find_one_and_update(
        {"_id": oid(id), "status": "issued"},
        {"$set": {"status": "returned"}}
    )
    if loan:
        db.books.update_one({"_id": oid(loan["book_id"])}, {"$inc": {"copies": 1}})
    return jsonify(ok=bool(loan))

@app.post("/api/renew/<id>")
def renew_book(id):
    new_due = (datetime.date.today() + datetime.timedelta(days=21)).strftime("%b %d, %Y")
    db.loans.update_one({"_id": oid(id)}, {"$set": {"due": new_due}})
    return jsonify(ok=True, due=new_due)

@app.get("/api/loans")
def loans():
    out = []
    for l in db.loans.find():
        m = db.members.find_one({"_id": oid(l["member_id"])}) or {}
        b = db.books.find_one({"_id": oid(l["book_id"])}) or {}
        out.append({
            **ser(l),
            "member": m.get("name", "Documentation Demo Student"),
            "studentId": m.get("studentId", "DOC-DEMO-001"),
            "book": b.get("title", "Advanced Engineering Mathematics"),
            "author": b.get("author", "Erwin Kreyszig"),
            "accession": l.get("accession") or b.get("accession", "ACC-002-02")
        })
    return jsonify(out)

# ---------- Recommendations (Neo4j + MongoDB Metadata Fallback) ----------
@app.get("/api/recommend/<member_id>")
def recommend(member_id):
    people = cypher("""MATCH (m:Member {id:$id})-[:READ]->(:Book)<-[:READ]-(o:Member)-[:READ]->(rec:Book)
        WHERE NOT (m)-[:READ]->(rec)
        RETURN rec.title AS title, count(DISTINCT o) AS readers ORDER BY readers DESC LIMIT 5""", id=member_id)
    genre = cypher("""MATCH (m:Member {id:$id})-[:READ]->(:Book)-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(rec:Book)
        WHERE NOT (m)-[:READ]->(rec)
        RETURN rec.title AS title, collect(DISTINCT g.name) AS genres LIMIT 5""", id=member_id)

    read_book_ids = [oid(l["book_id"]) for l in db.loans.find({"member_id": member_id})]
    fallback_books = list(db.books.find({"_id": {"$nin": read_book_ids}}).limit(4))
    if not fallback_books:
        fallback_books = list(db.books.find().limit(4))

    return jsonify(
        also_read_by_similar_members=people,
        same_genre=genre,
        catalog_recommendations=[ser(b) for b in fallback_books]
    )

if __name__ == "__main__":
    seed_initial_data()
    app.run(debug=True)