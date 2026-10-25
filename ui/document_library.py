from pathlib import Path
import streamlit as st
from database import metadata_db as db
from services.document_service import save_upload, SUPPORTED
from services.ingestion_service import ingest_document
from services.vector_store import delete_document_chunks

def render_document_library():
    st.title("Document library")
    st.write("Upload documents, index their content locally, and manage their status.")
    uploads = st.file_uploader(
        "Choose files",
        type=[x.lstrip(".") for x in sorted(SUPPORTED)],
        accept_multiple_files=True,
        help="Supported: PDF, DOCX, TXT, MD, XLSX, XLSM and CSV."
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        enable_ocr = st.checkbox("OCR scanned PDF pages", value=True)
    with col2:
        st.caption("OCR requires Tesseract OCR installed on Windows.")
    if st.button("Save and index uploads", type="primary", disabled=not uploads):
        for uploaded in uploads or []:
            try:
                candidate = save_upload(uploaded)
                existing = db.get_document_by_hash(candidate["file_hash"])
                if existing:
                    Path(candidate["stored_path"]).unlink(missing_ok=True)
                    st.info(f"Already uploaded: {existing['filename']}")
                    continue
                db.add_document(candidate)
                with st.spinner(f"Indexing {candidate['filename']}..."):
                    count = ingest_document(candidate["id"], enable_ocr=enable_ocr)
                st.success(f"Indexed {candidate['filename']} ({count} chunks)")
            except Exception as exc:
                st.error(f"{uploaded.name}: {exc}")
        st.rerun()

    st.subheader("Stored documents")
    docs = db.list_documents()
    if not docs:
        st.info("No documents uploaded yet.")
        return
    for doc in docs:
        with st.container(border=True):
            a, b, c = st.columns([5, 2, 1])
            with a:
                st.markdown(f"**{doc['filename']}**")
                st.caption(f"{doc['file_type'].upper()} · {doc['file_size']:,} bytes · {doc['chunk_count']} chunks")
                if doc.get("error"):
                    st.error(doc["error"])
            with b:
                st.write(f"Status: **{doc['status']}**")
                if doc["status"] != "indexed":
                    if st.button("Re-index", key=f"reindex_{doc['id']}"):
                        try:
                            with st.spinner("Indexing document..."):
                                count = ingest_document(doc["id"], enable_ocr=enable_ocr if 'enable_ocr' in locals() else True)
                            st.success(f"Indexed {count} chunks")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
            with c:
                if st.button("Delete", key=f"delete_{doc['id']}"):
                    delete_document_chunks(doc["id"])
                    Path(doc["stored_path"]).unlink(missing_ok=True)
                    db.delete_document_record(doc["id"])
                    st.session_state.selected_doc_ids = [
                        x for x in st.session_state.get("selected_doc_ids", []) if x != doc["id"]
                    ]
                    st.rerun()
