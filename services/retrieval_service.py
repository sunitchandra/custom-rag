from services.ollama_service import embed_texts
from services.vector_store import search

def retrieve(question, document_ids, top_k=5, embedding_model=None, max_distance=None):
    if not document_ids:
        return []
    vector = embed_texts([question], model=embedding_model)[0]
    rows = search(vector, document_ids, top_k=top_k)
    if max_distance is not None:
        rows = [r for r in rows if r["distance"] is None or r["distance"] <= float(max_distance)]
    return rows
