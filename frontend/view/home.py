import streamlit as st
from pathlib import Path
import base64

def run():
    st.title("🎬 Welcome to the Media Analysis Tool")

    # Dynamically resolve path to the video file
    video_path = Path(__file__).parent.parent / "assets" / "hero_video.mp4"

    if video_path.exists():
        video_bytes = video_path.read_bytes()
        video_base64 = base64.b64encode(video_bytes).decode()

        st.markdown(
            f"""
            <style>
                .video-wrapper {{
                    position: relative;
                    width: 100%;
                    padding-top: 66.66%; /* 3:2 Aspect Ratio → 2/3 = 66.66% */
                    overflow: hidden;
                    border-radius: 16px;
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
                    margin-bottom: 2rem;
                }}

                .video-wrapper video {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                }}
            </style>

            <div class="video-wrapper">
                <video autoplay muted loop playsinline>
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning(f"⚠️ Could not find hero video at: {video_path}")

    st.markdown("### 🚀 Get started by selecting a view from the left sidebar.")
    st.caption("Analyze images and videos with AI, extract insights, and explore with RAG-powered search.")
