"""Streamlit admin dashboard"""
import streamlit as st
import requests
import pandas as pd

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
""")

st.markdown("---")

st.subheader("📊 Live Statistics")

API_URL = "http://localhost:8000"

col1, col2, col3, col4 = st.columns(4)

try:
    response = requests.get(f"{API_URL}/api/v1/analytics/stats")
    if response.status_code == 200:
        stats = response.json()
        
        with col1:
            st.metric("Total Queries", stats.get("total_queries", 0))
        with col2:
            st.metric("Successful Queries", stats.get("successful_queries", 0))
        with col3:
            st.metric("Avg Confidence", f"{stats.get('average_confidence', 0):.1%}")
        with col4:
            st.metric("Avg Response Time", f"{stats.get('average_response_time_ms', 0):.0f}ms")
    else:
        st.error("Failed to fetch analytics")
except Exception as e:
    st.error(f"API connection error: {e}")
    st.info("Make sure the API is running at http://localhost:8000")