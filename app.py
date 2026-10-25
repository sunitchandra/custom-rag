import streamlit as st
from config.settings import APP_TITLE
from database.metadata_db import init_db
from ui.sidebar import render_sidebar
from ui.document_library import render_document_library
from ui.collections import render_collections
from ui.chat import render_chat
from ui.settings_page import render_settings
from services.logging_config import configure_logging

configure_logging()

st.set_page_config(page_title=APP_TITLE, page_icon="📚", layout="wide")
init_db()

if "page" not in st.session_state:
    st.session_state.page = "Chat"
if "selected_doc_ids" not in st.session_state:
    st.session_state.selected_doc_ids = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

render_sidebar()
page = st.session_state.page
if page == "Chat":
    render_chat()
elif page == "Documents":
    render_document_library()
elif page == "Collections":
    render_collections()
elif page == "Settings":
    render_settings()
