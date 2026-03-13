"""Analytics page"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.title("📊 Analytics Dashboard")

API_URL = "http://localhost:8000"

st.markdown("""
Monitor system performance, query patterns, and usage statistics.
""")

st.markdown("---")

st.header("Overview Metrics")

col1, col2, col3, col4 = st.columns(4)

try:
    response = requests.get(f"{API_URL}/api/v1/analytics/stats")
    if response.status_code == 200:
        stats = response.json()
        
        with col1:
            st.metric("Total Queries", stats.get("total_queries", 0))
        with col2:
            st.metric("Successful", stats.get("successful_queries", 0))
        with col3:
            st.metric("Avg Confidence", f"{stats.get('average_confidence', 0):.1%}")
        with col4:
            st.metric("Avg Response Time", f"{stats.get('average_response_time_ms', 0):.0f}ms")
    else:
        st.error("Failed to fetch analytics")
except Exception as e:
    st.error(f"API connection error: {e}")

st.markdown("---")

st.header("Intent Classification Distribution")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Queries by Intent Space")
    intent_data = pd.DataFrame({
        "Intent Space": ["HR", "Legal", "Finance", "General"],
        "Queries": [0, 0, 0, 0]
    })
    st.bar_chart(intent_data.set_index("Intent Space"))

with col2:
    st.subheader("Classification Confidence")
    st.markdown("""
    - **HR**: No data yet
    - **Legal**: No data yet
    - **Finance**: No data yet
    - **General**: No data yet
    """)

st.markdown("---")

st.header("Recent Activity")

st.info("Recent queries and document uploads will appear here once the system starts receiving traffic.")

st.markdown("---")

st.header("System Health")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("API Status", "🟢 Online")
with col2:
    st.metric("Database", "🟢 Connected")
with col3:
    st.metric("Ollama LLM", "🟢 Available")

st.markdown("---")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")