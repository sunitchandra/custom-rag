import streamlit as st
from config import settings
from services.ollama_service import list_models
from services.document_service import pytesseract

def render_settings():
    st.title("RAG settings")
    st.write("These settings are stored in the current Streamlit session. Set environment variables in `.env` for default model names.")
    try:
        installed = list_models()
        st.success(f"Ollama is reachable. {len(installed)} model(s) found.")
    except Exception as exc:
        installed = []
        st.error(f"Could not connect to Ollama at {settings.OLLAMA_HOST}: {exc}")
    model_options = installed or [settings.DEFAULT_CHAT_MODEL]
    embedding_options = installed or [settings.DEFAULT_EMBEDDING_MODEL]
    st.session_state.chat_model = st.selectbox(
        "Chat model", model_options,
        index=model_options.index(st.session_state.get("chat_model", settings.DEFAULT_CHAT_MODEL))
        if st.session_state.get("chat_model", settings.DEFAULT_CHAT_MODEL) in model_options else 0
    )
    st.session_state.embedding_model = st.selectbox(
        "Embedding model", embedding_options,
        index=embedding_options.index(st.session_state.get("embedding_model", settings.DEFAULT_EMBEDDING_MODEL))
        if st.session_state.get("embedding_model", settings.DEFAULT_EMBEDDING_MODEL) in embedding_options else 0
    )
    st.session_state.chunk_size = st.slider("Chunk size (characters)", 300, 1800, int(st.session_state.get("chunk_size", 900)), 100)
    st.session_state.chunk_overlap = st.slider("Chunk overlap (characters)", 0, 400, int(st.session_state.get("chunk_overlap", 150)), 25)
    st.session_state.top_k = st.slider("Retrieved chunks (top-K)", 1, 12, int(st.session_state.get("top_k", 5)))
    st.session_state.temperature = st.slider("Answer temperature", 0.0, 1.0, float(st.session_state.get("temperature", 0.1)), 0.05)
    st.session_state.max_distance = st.number_input(
        "Optional maximum cosine distance (0 disables threshold)",
        min_value=0.0, max_value=2.0, value=float(st.session_state.get("max_distance", 0.0)), step=0.05,
        help="Lower distance means more similar. Threshold is applied after vector search."
    )
    st.divider()
    try:
        st.info(f"Tesseract executable: {pytesseract.pytesseract.tesseract_cmd or 'found via PATH'}")
    except Exception:
        st.caption("Tesseract status will be checked when OCR is needed.")
