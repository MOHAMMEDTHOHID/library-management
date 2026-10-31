# Library Management and Book Recommendation System (Flask + MongoDB + Neo4j)

A full-stack polyglot NoSQL application that combines traditional library inventory and circulation management with relationship-aware book recommendations.

---

## 🏗️ Architecture & Why Two Databases?

This project implements a **Polyglot Persistence** pattern, leveraging two specialized NoSQL databases for the exact workloads they handle best:

* **MongoDB (Document Database - System of Record):** Ideal for flexible schema documents and transactional updates. It stores bibliographic data, physical inventory copy counts, member profiles, and active loan statuses.
* **Neo4j (Property Graph Database - Recommendation Index):** Ideal for deep relationship traversal. Instead of writing complex SQL multi-joins, generating "readers like you also read" recommendations becomes a single efficient Cypher pattern traversal.

### Data Storage Responsibilities

| Data Domain / Entity | MongoDB (`library` database) | Neo4j Graph Index |
| :--- | :--- | :--- |
| **Core Entities** | Books, members, loans (with copies, dates, and status)[cite: 4] | Node IDs, titles, and names only[cite: 4] |
| **Relationships** | *No (handled via document references)*[cite: 4] | `(:Member)-[:READ]->(:Book)`, `(:Book)-[:WRITTEN_BY]->(:Author)`, `(:Book)-[:IN_GENRE]->(:Genre)`[cite: 4] |

---

## 🚀 Quick Setup & Installation

### 1. Prerequisites
* Python 3.10+ installed on your system.
* Active **MongoDB** instance (Local or MongoDB Atlas)[cite: 4].
* Active **Neo4j** instance (Local or Neo4j AuraDB)[cite: 4].

### 2. Install Dependencies
Open your terminal in the project root folder and install the required Python packages[cite: 4, 5]:
```bash
pip install -r requirements.txt
pip install "pymongo[srv]" certifi.

### Project Structure
library_project/
├── templates/
│   └── index.html       # Frontend single-page workspace UI[cite: 2]
├── app.py               # Flask backend API, MongoDB CRUD, and Neo4j driver[cite: 1]
├── queries.md           # Reference Cypher and MongoDB shell queries[cite: 3]
├── README.md            # Project documentation and setup guide[cite: 4]
└── requirements.txt     # Python dependencies (Flask, PyMongo, Neo4j)[cite: 4, 5]
