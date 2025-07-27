import streamlit as st
from classes.api_client import analyze_media

def run():
    st.header("🎥📸 Media Analysis")
    st.write("Upload an image or video to generate a summary and insights from the media.")

    uploaded_file = st.file_uploader("Upload your media file",
    type=[
        # Image types
        "png", "jpg", "jpeg", "webp", 
        # Video types
        "mp4", "mov", "avi", "mkv",
        # Audio types
        "mp3", "wav", "m4a"
    ])


    if uploaded_file and st.button("Analyze Media"):
        with st.spinner("🔎 Analyzing media content..."):
            result = analyze_media(uploaded_file)

        if result:
            st.success("✅ Analysis complete!")
            st.markdown(f"**Summary:**\n\n{result.get('summary', 'No summary available')}")

            # Show transcript if available
            if transcript := result.get("transcript"):
                st.markdown("**🗣️ Transcript:**")
                st.text(transcript)

            # Show metadata
            if metadata := result.get("media_metadata"):
                st.markdown("**🧾 Media Metadata:**")
                st.json(metadata)

            # Show raw debug fields (if any)
            if "ollama_raw" in result or "combined_visual" in result:
                with st.expander("🛠️ Debug Info"):
                    st.json({k: v for k, v in result.items() if k in ["ollama_raw", "combined_visual"]})

            st.subheader("📄 Full Result")
            st.json(result)
