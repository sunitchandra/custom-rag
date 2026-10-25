import streamlit as st
from database import metadata_db as db

def render_collections():
    st.title("Document collections")
    st.write("Create reusable groups of documents. Select collections in the sidebar to include their documents in retrieval.")
    with st.form("create_collection"):
        name = st.text_input("Collection name", placeholder="e.g. Project Documentation")
        description = st.text_input("Description (optional)")
        submitted = st.form_submit_button("Create collection")
    if submitted:
        if not name.strip():
            st.warning("Enter a collection name.")
        else:
            try:
                db.create_collection(name, description)
                st.success("Collection created.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not create collection: {exc}")

    docs = db.list_documents()
    collections = db.list_collections()
    if not collections:
        st.info("Create a collection to start grouping documents.")
        return
    for collection in collections:
        with st.expander(f"{collection['name']} ({collection['document_count']} documents)", expanded=False):
            st.caption(collection.get("description") or "No description")
            available = [d for d in docs if d["status"] == "indexed"]
            labels = {d["id"]: d["filename"] for d in available}
            current = [d for d in db.collection_document_ids(collection["id"]) if d in labels]
            chosen = st.multiselect(
                "Documents in this collection",
                options=list(labels.keys()),
                default=current,
                format_func=lambda x: labels[x],
                key=f"members_{collection['id']}"
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Save membership", key=f"save_{collection['id']}"):
                    db.set_collection_documents(collection["id"], chosen)
                    st.success("Collection updated.")
                    st.rerun()
            with c2:
                if st.button("Delete collection", key=f"del_{collection['id']}"):
                    db.delete_collection(collection["id"])
                    st.rerun()
