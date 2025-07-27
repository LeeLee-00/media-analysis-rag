import streamlit as st
from classes.api_client import keyword_search

def run():
    st.title("🔤 Keyword Search")
    st.markdown("Search across AI-generated summaries and transcripts for your media files.")

    keyword_query = st.text_input("Enter keywords to search:")
    show_metadata = st.checkbox("Show metadata for each result", value=False)
    show_debug = st.checkbox("Show raw debug info", value=False)

    if st.button("Search") and keyword_query:
        with st.spinner("Searching..."):
            response = keyword_search({"query": keyword_query})

        if response and response.get("results"):
            st.success(f"✅ Found {len(response['results'])} matching result(s).")

            for idx, result in enumerate(response["results"]):
                with st.expander(f"{idx+1}. {result['filename']} — {result['media_type']}"):
                    # --- Summary ---
                    st.markdown("**📝 Summary:**")
                    st.markdown(result.get("summary", "_No summary available._"))

                    # --- Transcript ---
                    transcript = result.get("transcript", "")
                    if transcript:
                        st.markdown("**📄 Transcript:**")
                        st.text_area("Transcript", transcript, height=150)
                        st.download_button("⬇️ Download Transcript", transcript, f"{result['filename']}_transcript.txt")
                    else:
                        st.info("🧾 No transcript available for this media.")

                    # --- Metadata ---
                    metadata = result.get("media_metadata")
                    if show_metadata:
                        st.markdown("🔍 **Metadata:**")
                        if metadata and isinstance(metadata, dict):
                            st.json(metadata)
                        else:
                            st.warning("ℹ️ No metadata available for this media.")

                    # --- Raw API Data (Debugging) ---
                    if show_debug:
                        st.markdown("🛠️ **Raw API Response:**")
                        st.code(result)

        else:
            st.warning("No matches found.")
