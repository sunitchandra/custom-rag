import streamlit as st
from database import metadata_db as db
from services.rag_service import ask

def render_chat():
    st.title("Chat with your documents")
    st.caption("Answers are generated locally by Ollama and grounded in the selected document sources.")
    if not st.session_state.get("selected_doc_ids"):
        st.warning("Select one or more indexed documents or collections in the sidebar to begin.")
    for index, item in enumerate(st.session_state.chat_history):
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
            if item["role"] == "assistant" and item.get("sources"):
                with st.expander(f"Sources used ({len(item['sources'])})"):
                    for source in item["sources"]:
                        st.markdown(f"**{source['label']} — {source['filename']}** · {source['location']}")
                        st.write(source["text"])
                        st.caption(f"Cosine distance: {source['distance']:.3f}" if source.get("distance") is not None else "")
    question = st.chat_input("Ask a question about the selected documents...")
    if question:
        selected = list(dict.fromkeys(st.session_state.get("selected_doc_ids", [])))
        indexed_ids = {d["id"] for d in db.list_documents() if d["status"] == "indexed"}
        selected = [doc_id for doc_id in selected if doc_id in indexed_ids]
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        if not selected:
            answer = {"answer": "Please select at least one indexed document or collection in the sidebar.", "sources": []}
        else:
            with st.chat_message("assistant"):
                with st.spinner("Searching selected documents and generating an answer locally..."):
                    try:
                        answer = ask(
                            question=question,
                            document_ids=selected,
                            chat_model=st.session_state.get("chat_model"),
                            embedding_model=st.session_state.get("embedding_model"),
                            top_k=st.session_state.get("top_k", 5),
                            temperature=st.session_state.get("temperature", 0.1),
                            max_distance=st.session_state.get("max_distance", 0.0) or None,
                            history=st.session_state.chat_history[:-1],
                        )
                    except Exception as exc:
                        answer = {"answer": f"An error occurred: {exc}", "sources": []}
                st.markdown(answer["answer"])
                if answer["sources"]:
                    with st.expander(f"Sources used ({len(answer['sources'])})"):
                        for source in answer["sources"]:
                            st.markdown(f"**{source['label']} — {source['filename']}** · {source['location']}")
                            st.write(source["text"])
        st.session_state.chat_history.append({
            "role": "assistant", "content": answer["answer"], "sources": answer["sources"]
        })
        st.rerun()
