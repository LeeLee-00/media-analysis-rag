import streamlit as st
import requests
from view import home, media_analysis, searches

# === Page Config (must be first Streamlit command) ===
st.set_page_config(page_title="Media Analysis Tool", layout="wide")

# === Sidebar Navigation ===
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a tool:", ["🏠 Home", "🎥 📸 Media Analysis", "🔍 RAG/Keyword Search"])

# === Backend Config ===
# BACKEND_URL = "http://multi-media-analysis:8000"
BACKEND_URL = "http://localhost:8000"
# st.sidebar.write("#### Backend URL")
st.sidebar.code(BACKEND_URL)

# === Backend Connection Test ===
if st.sidebar.button("🔌 Test Backend Connection"):
    try:
        response = requests.get(f"{BACKEND_URL}/docs")
        if response.status_code == 200:
            st.sidebar.success("✅ Connected to backend!")
        else:
            st.sidebar.warning(f"⚠️ Backend responded with status: {response.status_code}")
    except Exception as e:
        st.sidebar.error(f"❌ Failed to connect: {e}")
        st.sidebar.info("Make sure your backend server is running.")

# Function to analyze media
def analyze_media(file, media_type, analysis_type=None):
    """Send media to backend for analysis"""
    # Backend endpoints from your files: "/image" and "/video" 
    endpoint = f"{BACKEND_URL}/analyze/{media_type}"
    
    files = {"file": (file.name, file.getvalue(), file.type)}
    params = {}
    
    if analysis_type and analysis_type != "Default":
        params["analysis_type"] = analysis_type
    
    try:
        with st.spinner(f"Analyzing {media_type}..."):
            response = requests.post(endpoint, files=files, params=params)
            
            if response.status_code != 200:
                st.error(f"Error: {response.text}")
                return None
                
            return response.json()
    except Exception as e:
        st.sidebar.error(f"❌ Failed to connect: {e}")
        st.sidebar.info("Make sure your backend server is running.")

# === Page Routing ===
if page == "🏠 Home":
    home.run()
elif page == "🎥 📸 Media Analysis":
    media_analysis.run()
elif page == "🔍 RAG/Keyword Search":
    searches.run()

# === Footer ===
st.sidebar.markdown("---")
st.sidebar.caption("Media Analysis Tool v1.0")
