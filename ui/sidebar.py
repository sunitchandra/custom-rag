import streamlit as st
from database import metadata_db as db

def render_sidebar():
    with st.sidebar:
        st.title("📚 Local RAG")
        st.caption("Private document assistant")
        st.radio("Navigate", ["Chat", "Documents", "Collections", "Settings"],
                 key="page", label_visibility="collapsed")
        st.divider()
        docs = db.list_documents()
        indexed = [d for d in docs if d["status"] == "indexed"]
        st.subheader("Chat sources")
        st.caption(f"{len(indexed)} indexed document(s) available")
        if not indexed:
            st.info("Upload and index documents first.")
            st.session_state.selected_doc_ids = []
            return
        doc_labels = {d["id"]: f'{d["filename"]}' for d in indexed}
        current = [d for d in st.session_state.get("selected_doc_ids", []) if d in doc_labels]
        selected = st.multiselect(
            "Individual documents",
            options=list(doc_labels.keys()),
            default=current,
            format_func=lambda x: doc_labels[x],
            help="Only these selected documents will be searched.",
        )
        st.session_state.selected_doc_ids = selected
        collections = db.list_collections()
        if collections:
            labels = {str(c["id"]): c["name"] for c in collections}
            chosen = st.multiselect("Collections", list(labels.keys()), format_func=lambda x: labels[x])
            if chosen:
                expanded = set(st.session_state.selected_doc_ids)
                for collection_id in chosen:
                    expanded.update(db.collection_document_ids(int(collection_id)))
                st.session_state.selected_doc_ids = sorted(expanded.intersection(doc_labels))
        st.caption(f"{len(st.session_state.selected_doc_ids)} document(s) in retrieval scope")
        if st.button("Clear chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
