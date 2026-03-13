"""Documents management page"""
import streamlit as st
import requests

st.title("📄 Document Management")

# Upload section
st.header("Upload Document")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
intent_space = st.selectbox(
    "Intent Space",
    ["HR", "Legal", "Finance", "General"]
)

if uploaded_file and st.button("Upload"):
    st.info("Upload functionality will be implemented")

# Document list
st.header("Uploaded Documents")
st.info("Document list will appear here")