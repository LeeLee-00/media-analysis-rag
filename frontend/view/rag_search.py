import streamlit as st
from classes.api_client import rag_search_query


def run():
    st.title("📚 RAG Search")
    st.markdown("Ask a question about your media files. Our AI will find relevant documents and generate an answer using RAG.")

    # Session state setup
    if "rag_history" not in st.session_state:
        st.session_state.rag_history = []

    # Optional clear button
    if st.button("🧹 Clear Conversation", key="clear_chat"):
        st.session_state.rag_history = []

    # Chat input
    query = st.chat_input("Ask a question about the media files...")

    if query:
        with st.spinner("Running RAG search..."):
            payload = {
                "query": query,
                "prompt_template": "Based on the following media files and their summaries/transcripts, answer the question:",
                "top_k": 5,
                "score_threshold": 1.25,
                "fallback_to_keyword": True,
                "debug": False
            }
            response = rag_search_query(payload)

        # Save message in session
        st.session_state.rag_history.append({"question": query, "response": response})

    # Display message history
    for entry in st.session_state.rag_history[::-1]:
        with st.chat_message("user"):
            st.markdown(entry["question"])

        with st.chat_message("assistant"):
            response = entry["response"]

            if "answer" in response:
                st.markdown(response["answer"])
            else:
                st.warning("⚠️ No answer generated.")

            for doc in response.get("supporting_documents", []):
                with st.expander("📁 Supporting Media"):
                    st.markdown(f"**Filename:** `{doc['filename']}`")
                    st.markdown(f"**Type:** `{doc['media_type']}`")
                    
                    if doc.get("summary"):
                        st.markdown(f"**Summary:** {doc['summary']}")

                    # Transcript download
                    transcript_text = doc.get("transcript", "").strip()

                    if transcript_text:
                        st.download_button(
                            label="📥 Download Transcript",
                            data=transcript_text,
                            file_name=f"{doc['filename'].rsplit('.', 1)[0]}_transcript.txt",
                            mime="text/plain"
                        )
                    else:
                        st.info("📄 No transcript available for this media.")


