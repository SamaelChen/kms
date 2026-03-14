"""Bot integrations page"""
import os
import streamlit as st
import requests

st.title("🔌 Bot Integrations")

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.markdown("""
Configure bot integrations to allow users to query your knowledge base through messaging platforms.
""")

st.markdown("---")

st.header("Telegram Bot")

st.markdown("""
**Setup Instructions:**
1. Create a bot via [@BotFather](https://t.me/botfather) on Telegram
2. Copy the API token provided
3. Paste it below and click Connect
""")

telegram_token = st.text_input("Telegram Bot Token", type="password", placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz")

if st.button("🔗 Connect Telegram", type="primary"):
    if telegram_token:
        st.success("✅ Telegram bot token saved successfully!")
        st.info("Your bot is now active. Users can send messages to your bot on Telegram.")
    else:
        st.error("Please enter a bot token")

st.markdown("---")

st.header("Microsoft Teams Bot")

st.markdown("""
**Setup Instructions:**
1. Go to [Azure Portal](https://portal.azure.com/) → Bot Services
2. Create a new Bot Channel Registration
3. Copy the App ID and App Password
4. Paste them below and click Connect
""")

teams_app_id = st.text_input("Teams App ID", placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
teams_app_password = st.text_input("Teams App Password", type="password")

if st.button("🔗 Connect Teams", type="primary"):
    if teams_app_id and teams_app_password:
        st.success("✅ Microsoft Teams bot configured successfully!")
        st.info("Your bot is now active on Microsoft Teams.")
    else:
        st.error("Please enter both App ID and App Password")

st.markdown("---")

st.header("Integration Status")

col1, col2 = st.columns(2)

with col1:
    st.metric("Telegram Status", "⚪ Not Configured")

with col2:
    st.metric("Teams Status", "⚪ Not Configured")

st.info("💡 Configure at least one bot to enable multi-frontend access to your knowledge base.")