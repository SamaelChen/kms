"""Bot integrations page"""
import streamlit as st

st.title("🔌 Bot Integrations")

st.header("Telegram Bot")
telegram_token = st.text_input("Telegram Bot Token", type="password")
if st.button("Connect Telegram"):
    st.info("Connection will be implemented")

st.header("Microsoft Teams Bot")
teams_app_id = st.text_input("Teams App ID")
teams_app_password = st.text_input("Teams App Password", type="password")
if st.button("Connect Teams"):
    st.info("Connection will be implemented")