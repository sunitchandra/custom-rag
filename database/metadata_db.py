import sqlite3
from contextlib import contextmanager
from config.settings import SQLITE_PATH

@contextmanager
def connection():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with connection() as conn:
        conn.executescript("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            file_hash TEXT NOT NULL UNIQUE,
            file_type TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'uploaded',
            chunk_count INTEGER NOT NULL DEFAULT 0,
            error TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS collection_documents (
            collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
            document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            PRIMARY KEY (collection_id, document_id)
        );
        """)

def list_documents():
    with connection() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()]

def get_document(doc_id):
    with connection() as conn:
        row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
        return dict(row) if row else None

def get_document_by_hash(file_hash):
    with connection() as conn:
        row = conn.execute("SELECT * FROM documents WHERE file_hash=?", (file_hash,)).fetchone()
        return dict(row) if row else None

def add_document(doc):
    with connection() as conn:
        conn.execute("""INSERT INTO documents
            (id, filename, stored_path, file_hash, file_type, file_size, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (doc["id"], doc["filename"], doc["stored_path"], doc["file_hash"],
             doc["file_type"], doc["file_size"], doc.get("status", "uploaded")))

def update_document(doc_id, **fields):
    allowed = {"status", "chunk_count", "error", "filename", "stored_path"}
    fields = {k: v for k, v in fields.items() if k in allowed}
    if not fields:
        return
    clause = ", ".join(f"{k}=?" for k in fields)
    with connection() as conn:
        conn.execute(f"UPDATE documents SET {clause} WHERE id=?",
                     (*fields.values(), doc_id))

def delete_document_record(doc_id):
    with connection() as conn:
        conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))

def list_collections():
    with connection() as conn:
        rows = conn.execute("""
            SELECT c.*, COUNT(cd.document_id) AS document_count
            FROM collections c LEFT JOIN collection_documents cd ON cd.collection_id=c.id
            GROUP BY c.id ORDER BY c.name
        """).fetchall()
        return [dict(r) for r in rows]

def create_collection(name, description=""):
    with connection() as conn:
        cur = conn.execute("INSERT INTO collections(name, description) VALUES (?, ?)",
                           (name.strip(), description.strip()))
        return cur.lastrowid

def collection_document_ids(collection_id):
    with connection() as conn:
        return [r["document_id"] for r in conn.execute(
            "SELECT document_id FROM collection_documents WHERE collection_id=?",
            (collection_id,)).fetchall()]

def set_collection_documents(collection_id, doc_ids):
    with connection() as conn:
        conn.execute("DELETE FROM collection_documents WHERE collection_id=?", (collection_id,))
        conn.executemany("INSERT OR IGNORE INTO collection_documents(collection_id, document_id) VALUES (?, ?)",
                         [(collection_id, d) for d in doc_ids])

def delete_collection(collection_id):
    with connection() as conn:
        conn.execute("DELETE FROM collections WHERE id=?", (collection_id,))
