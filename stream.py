import streamlit as st
import requests

st.set_page_config(page_title="AI Model Builder", layout="wide")
st.title("🤖 ML Model Architect")

desc = st.text_area("Describe your ML model:", height=150)

if st.button("Build & Run Model"):
    if desc.strip():
        with st.status("🏗️ Building Environment (Installing Packages...)", expanded=True) as status:
            try:
                # 300 second timeout for heavy ML library installs
                res = requests.post("http://127.0.0.1:8000/create-and-run", json={"description": desc}, timeout=300)
                data = res.json()
                
                if data["status"] == "success":
                    status.update(label="✅ Bot Ready!", state="complete")
                    st.success("Your bot is running at http://localhost:8502")
                else:
                    st.error(data["message"])
            except Exception as e:
                st.error(f"Error: {e}. Ensure FastAPI is running.")