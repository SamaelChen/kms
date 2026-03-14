# Implementation Plan: Direct Chat Interface

**Source:** [Brainstorm Document](docs/brainstorms/2026-03-14-direct-chat-interface-brainstorm.md)  
**Date:** 2026-03-14  
**Estimated Effort:** 1-2 days

---

## Phase 1: Create Chat Page (Day 1)

### 1.1 Create Chat Page File
**File to create:**
- `admin-dashboard/pages/6_Chat.py`

**Structure:**
```python
import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

st.title("💬 Chat with Knowledge Base")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar options
with st.sidebar:
    st.header("Options")
    show_thinking = st.checkbox("Show thinking steps", value=False)
    if st.button("🗑️ Clear Chat", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()

# Chat display area
st.markdown("---")

# Display chat history
for i, msg in enumerate(st.session_state.chat_history):
    display_message(msg, msg_id=i)

# Input area
st.markdown("---")
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Your question",
            placeholder="Ask about company policies, procedures, etc...",
            label_visibility="collapsed"
        )
    with col2:
        submitted = st.form_submit_button("Send", use_container_width=True)
    
    if submitted and user_input.strip():
        process_message(user_input, show_thinking)
```

### 1.2 Message Display Function
**In `6_Chat.py`:**

```python
def display_message(msg: dict, msg_id: int):
    """Display a chat message with citations and feedback."""
    timestamp = msg.get("timestamp", "")
    time_str = datetime.fromisoformat(timestamp).strftime("%H:%M") if timestamp else ""
    
    if msg["role"] == "user":
        st.markdown(f"**🧑 You** ({time_str}):\n{msg['content']}")
    else:
        st.markdown(f"**🤖 Assistant** ({time_str}):\n{msg['content']}")
        
        # Citations
        citations = msg.get("citations", [])
        if citations:
            with st.expander(f"📚 Sources ({len(citations)})"):
                for citation in citations:
                    doc_name = citation.get("document_name", "Unknown")
                    preview = citation.get("text_preview", "")[:100]
                    st.markdown(f"- **{doc_name}**: {preview}...")
        
        # Feedback buttons
        feedback = msg.get("feedback")
        cols = st.columns([1, 1, 10])
        with cols[0]:
            if st.button("👍", key=f"up_{msg_id}", 
                        type="secondary" if feedback != "up" else "primary"):
                msg["feedback"] = "up"
                st.rerun()
        with cols[1]:
            if st.button("👎", key=f"down_{msg_id}",
                        type="secondary" if feedback != "down" else "primary"):
                msg["feedback"] = "down"
                st.rerun()
```

---

## Phase 2: Message Processing (Day 1)

### 2.1 Process Message Function
**In `6_Chat.py`:**

```python
def process_message(user_input: str, show_thinking: bool):
    """Process user message and get response."""
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })
    
    # Show thinking steps if enabled
    if show_thinking:
        with st.status("Processing your query...", expanded=True) as status:
            response_data = query_with_thinking(user_input, status)
    else:
        response_data = query_api(user_input)
    
    # Add assistant response to history
    if response_data:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_data.get("response", "No response"),
            "citations": response_data.get("citations", []),
            "thinking_steps": response_data.get("thinking_steps", []),
            "intent_classified": response_data.get("intent_classified", "General"),
            "confidence_score": response_data.get("confidence_score", 0),
            "feedback": None,
            "timestamp": datetime.now().isoformat()
        })
    else:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "❌ Sorry, I couldn't process your query. Please try again.",
            "citations": [],
            "feedback": None,
            "timestamp": datetime.now().isoformat()
        })
    
    st.rerun()
```

### 2.2 API Query Functions
**In `6_Chat.py`:**

```python
def query_api(query: str) -> dict:
    """Send query to API and return response."""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/queries/ask",
            json={
                "query": query,
                "frontend": "dashboard",
                "user_id": "dashboard_user"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def query_with_thinking(query: str, status) -> dict:
    """Query API with visible thinking steps."""
    status.write("🔍 Classifying intent...")
    
    # Call API
    status.write("📚 Searching knowledge base...")
    response_data = query_api(query)
    
    if response_data:
        status.write("✍️ Generating response...")
        intent = response_data.get("intent_classified", "General")
        confidence = response_data.get("confidence_score", 0)
        citations = len(response_data.get("citations", []))
        
        status.update(
            label=f"✓ Intent: {intent} ({confidence:.0%}) | {citations} sources",
            state="complete"
        )
    else:
        status.update(label="❌ Error", state="error")
    
    return response_data
```

---

## Phase 3: Welcome & Empty States (Day 1)

### 3.1 Welcome Message
**In `6_Chat.py`, before chat display:**

```python
# Welcome message for empty chat
if not st.session_state.chat_history:
    st.info("""
    👋 Welcome to the Knowledge Base Chat!
    
    I can help you find information from your uploaded documents.
    
    **Example questions:**
    - "What is the leave policy?"
    - "How do I file an expense report?"
    - "What are the working hours?"
    
    Type your question below to get started.
    """)
```

---

## Phase 4: Navigation & Integration (Day 1)

### 4.1 Update Dashboard Navigation
**File to modify:**
- `admin-dashboard/app.py`

**Changes:**
No changes needed - Streamlit automatically picks up new pages in the `pages/` directory.

### 4.2 Update Main Page Quick Links
**File to modify:**
- `admin-dashboard/app.py`

**Add to quick actions section:**
```python
cols = st.columns(4)
with cols[0]:
    if st.button("💬 Chat", use_container_width=True):
        st.switch_page("pages/6_Chat.py")
```

---

## Phase 5: Testing (Day 1-2)

### 5.1 Test Scenarios

**Test 1: Basic Chat Flow**
- Navigate to Chat page
- Type a query
- Verify response appears
- Check citations are shown

**Test 2: Thinking Steps**
- Enable "Show thinking steps"
- Send query
- Verify steps appear (intent, search, generate)

**Test 3: Feedback**
- Send query
- Click thumbs up
- Verify button state changes
- Click thumbs down
- Verify button state changes

**Test 4: Clear Chat**
- Send multiple messages
- Click "Clear Chat"
- Verify history is empty
- Verify welcome message appears

**Test 5: Session Persistence**
- Send message
- Navigate to another page
- Return to Chat
- Verify message still there

**Test 6: Error Handling**
- Stop API server
- Send query
- Verify error message shown

---

## Files Summary

### New Files (1):
1. `admin-dashboard/pages/6_Chat.py` - Chat interface page

### Modified Files (1):
1. `admin-dashboard/app.py` - Add quick link to chat

---

## Configuration

No configuration needed - uses existing API_URL from other dashboard pages.

---

## Dependencies

No new dependencies - uses existing:
- streamlit (already in dashboard)
- requests (already used)

---

## Success Criteria Checklist

- [ ] Chat page accessible at `/Chat` in dashboard
- [ ] Welcome message shown on first load
- [ ] User can type and send queries
- [ ] Responses display with answer text
- [ ] Source citations shown in expander
- [ ] Thinking steps visible when enabled
- [ ] Feedback buttons (👍 / 👎) functional
- [ ] Clear chat button works
- [ ] Chat history persists within session
- [ ] Quick link from home page works
- [ ] Responsive layout on different screen sizes
- [ ] Error handling for API failures

---

## Commands to Test

```bash
# Start the services
docker compose up -d

# Or manually:
# Terminal 1: uvicorn app.main:app --reload
# Terminal 2: streamlit run admin-dashboard/app.py

# Access chat:
# http://localhost:8501/Chat
```

---

## Next Steps After Completion

1. Test end-to-end flow
2. Consider adding:
   - Chat persistence to database
   - Export chat history
   - Suggested questions
   - File upload from chat

---

## Notes

- Chat history is ephemeral by design - resets on page refresh
- Feedback is session-only - not stored to database (for MVP)
- Uses existing query API - no backend changes needed
- Streamlit's session_state persists across page navigation but not refresh
