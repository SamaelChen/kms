import streamlit as st
import requests
from datetime import datetime
from typing import Optional

st.set_page_config(page_title="Chat", page_icon="💬")

API_URL = "http://localhost:8000"


def query_api(query: str) -> Optional[dict]:
    try:
        response = requests.post(
            f"{API_URL}/api/v1/queries/ask",
            json={
                "query": query,
                "frontend": "dashboard",
                "user_id": st.session_state.user_id
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Please make sure the backend is running at http://localhost:8000")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def query_with_thinking(query: str, status) -> Optional[dict]:
    status.write("🔍 Analyzing your question...")
    
    status.write("📚 Searching knowledge base for relevant documents...")
    response_data = query_api(query)
    
    if response_data:
        intent = response_data.get("intent_classified", "General")
        confidence = response_data.get("confidence_score", 0)
        citations_count = len(response_data.get("citations", []))
        
        status.write("✍️ Generating response based on found information...")
        
        status.update(
            label=f"✓ Complete | Intent: {intent} ({confidence:.0%}) | Sources: {citations_count}",
            state="complete"
        )
    else:
        status.update(label="❌ Error processing query", state="error")
    
    return response_data


def process_message(user_input: str, show_thinking: bool):
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })
    
    if show_thinking:
        with st.status("Processing your query...", expanded=True) as status:
            response_data = query_with_thinking(user_input, status)
    else:
        response_data = query_api(user_input)
    
    if response_data:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_data.get("response", "No response received."),
            "citations": response_data.get("citations", []),
            "intent_classified": response_data.get("intent_classified", "General"),
            "confidence_score": response_data.get("confidence_score", 0),
            "feedback": None,
            "timestamp": datetime.now().isoformat()
        })
    else:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "❌ Sorry, I couldn't process your query. Please make sure the API is running and try again.",
            "citations": [],
            "intent_classified": "Error",
            "confidence_score": 0,
            "feedback": None,
            "timestamp": datetime.now().isoformat()
        })
    
    st.rerun()


st.title("💬 Chat with Knowledge Base")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"


with st.sidebar:
    st.header("Options")
    show_thinking = st.checkbox("Show thinking steps", value=False)
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Session Info**")
    st.text(f"Messages: {len(st.session_state.chat_history)}")
    st.text(f"User ID: {st.session_state.user_id}")


if not st.session_state.chat_history:
    st.info("""
    👋 Welcome to the Knowledge Base Chat!
    
    I can help you find information from your uploaded documents.
    Just type your question below and I'll search through the knowledge base.
    
    **Example questions:**
    - "What is the leave policy?"
    - "How do I file an expense report?"
    - "What are the company working hours?"
    - "How do I request time off?"
    
    Type your question below to get started!
    """)


st.markdown("---")

for i, msg in enumerate(st.session_state.chat_history):
    timestamp = msg.get("timestamp", "")
    time_str = ""
    if timestamp:
        try:
            time_str = datetime.fromisoformat(timestamp).strftime("%H:%M")
        except:
            time_str = ""
    
    if msg["role"] == "user":
        st.markdown(f"**🧑 You** *{time_str}*:\n{msg['content']}")
    else:
        st.markdown(f"**🤖 Assistant** *{time_str}*:\n{msg['content']}")
        
        citations = msg.get("citations", [])
        if citations:
            with st.expander(f"📚 Sources ({len(citations)})"):
                for citation in citations:
                    doc_name = citation.get("document_name", "Unknown")
                    preview = citation.get("text_preview", "")[:150]
                    st.markdown(f"- **{doc_name}**: {preview}...")
        
        intent = msg.get("intent_classified", "General")
        confidence = msg.get("confidence_score", 0)
        if confidence > 0:
            st.caption(f"Intent: {intent} (confidence: {confidence:.0%})")
        
        feedback = msg.get("feedback")
        cols = st.columns([1, 1, 8])
        
        with cols[0]:
            up_label = "👍" if feedback != "up" else "✅"
            if st.button(up_label, key=f"up_{i}", help="Helpful"):
                msg["feedback"] = "up"
                st.rerun()
        
        with cols[1]:
            down_label = "👎" if feedback != "down" else "❌"
            if st.button(down_label, key=f"down_{i}", help="Not helpful"):
                msg["feedback"] = "down"
                st.rerun()
    
    st.markdown("")


st.markdown("---")

with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Your question",
            placeholder="Ask about company policies, procedures, etc...",
            label_visibility="collapsed"
        )
    
    with col2:
        submitted = st.form_submit_button("Send", use_container_width=True, type="primary")
    
    if submitted and user_input and user_input.strip():
        with st.spinner("Processing..."):
            process_message(user_input.strip(), show_thinking)
