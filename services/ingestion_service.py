import hashlib
from services.document_service import extract_document
from services.chunking import split_text
from services.ollama_service import embed_texts
from services.vector_store import add_chunks, delete_document_chunks
from database import metadata_db as db

def ingest_document(doc_id, chunk_size=900, overlap=150, enable_ocr=True, embedding_model=None):
    doc = db.get_document(doc_id)
    if not doc:
        raise ValueError("Document metadata was not found.")
    db.update_document(doc_id, status="processing", error=None)
    try:
        sections = extract_document(doc["stored_path"], enable_ocr=enable_ocr)
        chunk_records = []
        for section in sections:
            chunks = split_text(section["text"], chunk_size, overlap)
            for i, chunk in enumerate(chunks):
                chunk_records.append((chunk, section, i))
        if not chunk_records:
            raise ValueError("No text could be extracted from this file.")
        # Remove old chunks before re-indexing.
        delete_document_chunks(doc_id)
        texts = [record[0] for record in chunk_records]
        embeddings = []
        batch_size = 24
        for start in range(0, len(texts), batch_size):
            embeddings.extend(embed_texts(texts[start:start + batch_size], model=embedding_model))
        ids, metadatas = [], []
        for idx, (chunk, section, section_chunk_index) in enumerate(chunk_records):
            ids.append(hashlib.sha256(f"{doc_id}:{idx}:{chunk}".encode("utf-8")).hexdigest())
            metadatas.append({
                "document_id": doc_id,
                "filename": doc["filename"],
                "source": section.get("source", "document"),
                "page": int(section["page"]) if section.get("page") is not None else -1,
                "chunk_index": idx,
            })
        add_chunks(ids, texts, embeddings, metadatas)
        db.update_document(doc_id, status="indexed", chunk_count=len(texts), error=None)
        return len(texts)
    except Exception as exc:
        db.update_document(doc_id, status="error", error=str(exc))
        raise
