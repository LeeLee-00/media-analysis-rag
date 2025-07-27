import streamlit as st
from view import rag_search, keyword_search


def run():
    st.title("🔎 Media Search")
    mode = st.radio("Choose search method:", ["RAG Search", "Keyword Search"], horizontal=True)

    if mode == "RAG Search":
        rag_search.run()
    else:
        keyword_search.run()