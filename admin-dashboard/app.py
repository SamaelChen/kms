"""Streamlit admin dashboard"""
import streamlit as st

st.set_page_config(
    page_title="IntelliKnow KMS Admin",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 IntelliKnow KMS Admin Dashboard")

st.sidebar.success("Select a page above")

st.markdown("""
## Welcome to IntelliKnow KMS

This admin dashboard allows you to:

- **📄 Manage Documents**: Upload, view, and delete knowledge base documents
- **🎯 Configure Intent Spaces**: Set up HR, Legal, Finance, and custom categories
- **🔌 Bot Integrations**: Configure Telegram and Microsoft Teams bots
- **📊 View Analytics**: Monitor query volume, classification accuracy, and more

### Quick Stats
""")

# Placeholder for stats
st.info("Connect to the API to see live statistics")