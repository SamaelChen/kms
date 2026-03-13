"""Documents management page"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.title("📄 Document Management")

API_URL = "http://localhost:8000"

# Upload section
st.header("Upload Document")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])

with col2:
    intent_space = st.selectbox(
        "Intent Space",
        ["HR", "Legal", "Finance", "General"]
    )

if uploaded_file and st.button("Upload Document", type="primary"):
    try:
        files = {"file": uploaded_file}
        data = {"intent_space": intent_space}
        
        response = requests.post(
            f"{API_URL}/api/v1/documents/upload",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ Document uploaded successfully!")
            st.json(result)
        else:
            st.error(f"Upload failed: {response.text}")
    except Exception as e:
        st.error(f"Error uploading: {e}")

st.markdown("---")

# Document list
st.header("Uploaded Documents")

try:
    response = requests.get(f"{API_URL}/api/v1/documents/")
    if response.status_code == 200:
        data = response.json()
        documents = data.get("documents", [])
        
        if documents:
            df = pd.DataFrame(documents)
            
            display_cols = ["filename", "intent_space", "status", "chunk_count", "created_at"]
            if all(col in df.columns for col in display_cols):
                st.dataframe(df[display_cols], use_container_width=True)
                
                st.subheader("Delete Document")
                doc_to_delete = st.selectbox(
                    "Select document to delete",
                    options=df["id"].tolist(),
                    format_func=lambda x: df[df["id"] == x]["filename"].iloc[0]
                )
                
                if st.button("🗑️ Delete Selected Document", type="secondary"):
                    try:
                        delete_response = requests.delete(f"{API_URL}/api/v1/documents/{doc_to_delete}")
                        if delete_response.status_code == 200:
                            st.success("Document deleted successfully!")
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {delete_response.text}")
                    except Exception as e:
                        st.error(f"Error deleting: {e}")
            else:
                st.dataframe(df, use_container_width=True)
        else:
            st.info("No documents uploaded yet. Upload your first document above!")
    else:
        st.error(f"Failed to fetch documents: {response.status_code}")
except Exception as e:
    st.error(f"API connection error: {e}")
    st.info("Make sure the API is running at http://localhost:8000")