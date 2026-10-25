import chromadb
from config.settings import CHROMA_PATH

_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        _collection = _client.get_or_create_collection(
            name="local_rag_documents",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

def add_chunks(ids, texts, embeddings, metadatas):
    if not ids:
        return
    collection = get_collection()
    collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

def delete_document_chunks(doc_id):
    get_collection().delete(where={"document_id": doc_id})

def search(query_embedding, document_ids, top_k=5):
    if not document_ids:
        return []
    collection = get_collection()
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=max(1, int(top_k)),
        where={"document_id": {"$in": document_ids}},
        include=["documents", "metadatas", "distances"],
    )
    rows = []
    ids = (result.get("ids") or [[]])[0]
    docs = (result.get("documents") or [[]])[0]
    metas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]
    for i, text in enumerate(docs):
        rows.append({
            "id": ids[i], "text": text, "metadata": metas[i] or {},
            "distance": distances[i] if i < len(distances) else None
        })
    return rows
