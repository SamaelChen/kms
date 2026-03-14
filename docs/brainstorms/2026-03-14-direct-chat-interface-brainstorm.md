---
date: 2026-03-14
topic: direct-chat-interface
---

# Direct Chat Interface

## What We're Building

A web-based chat interface integrated into the Streamlit admin dashboard. Users can chat directly with the knowledge base without needing Telegram or Teams accounts.

**Key Features:**
- Simple chat interface with text input and response display
- Source citations showing which documents were used
- Thinking/reasoning steps visibility (intent classification, document retrieval)
- Response feedback (thumbs up/down)
- Session-only history (resets on page refresh)

**Visual Style:** Simple text blocks (not chat bubbles), clean and minimal

## Why This Approach

**Chosen: Streamlit page with session-only storage**

- **Simplest implementation** - Leverages existing Streamlit dashboard
- **Consistent UI** - Same styling as other admin pages
- **No additional infrastructure** - Uses existing query API
- **Session-first** - YAGNI approach, can add persistence later if needed

**Rejected:**
- Standalone web app: Adds complexity, separate deployment
- WebSocket: Overkill for MVP, HTTP polling sufficient
- Persistent history: Adds database complexity, can add later

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Location** | New Streamlit page `6_Chat.py` in admin-dashboard/pages/ |
| **Storage** | Session state only (st.session_state) - resets on refresh |
| **Features** | Source citations, thinking steps, feedback - core value features |
| **No upload** | Document upload stays on Documents page - separation of concerns |
| **Style** | Simple text blocks - easier to implement, clean look |
| **API** | Uses existing `/api/v1/queries/ask` endpoint |

## User Flow

1. User navigates to Chat page
2. Sees empty chat or welcome message
3. Types query in text input at bottom
4. Clicks "Send" or presses Enter
5. Sees thinking steps (optional):
   - "Classifying intent..." → "HR (confidence: 0.85)"
   - "Searching knowledge base..." → "Found 3 relevant chunks"
   - "Generating response..."
6. Response appears with:
   - Answer text
   - Source citations (collapsible)
   - Feedback buttons (👍 / 👎)
7. Can continue conversation or clear chat

## Technical Approach

### Page Structure
```
admin-dashboard/pages/6_Chat.py

Layout:
- Header with title and "Clear Chat" button
- Chat history container (scrollable)
- Input area with text box and send button
- Sidebar with options (show thinking steps, etc.)
```

### Session State
```python
st.session_state.chat_history = [
    {
        "role": "user",
        "content": "What is the leave policy?",
        "timestamp": "2026-03-14T10:30:00"
    },
    {
        "role": "assistant",
        "content": "Based on the HR handbook...",
        "thinking_steps": [...],
        "citations": [...],
        "feedback": None,  # or "up"/"down"
        "timestamp": "2026-03-14T10:30:05"
    }
]
```

### Components

**Chat Message Display:**
```python
def display_message(msg):
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Assistant:** {msg['content']}")
        
        # Citations (collapsible)
        with st.expander("📚 Sources"):
            for citation in msg.get("citations", []):
                st.markdown(f"- {citation['document_name']}")
        
        # Feedback buttons
        col1, col2 = st.columns([1, 10])
        with col1:
            if st.button("👍", key=f"up_{msg_id}"):
                msg["feedback"] = "up"
        with col2:
            if st.button("👎", key=f"down_{msg_id}"):
                msg["feedback"] = "down"
```

**Thinking Steps (optional):**
```python
# Show in a status container
with st.status("Processing your query...", expanded=True) as status:
    st.write("Classifying intent...")
    intent = classify_intent(query)
    st.write(f"✓ Intent: {intent['space']} (confidence: {intent['confidence']:.2f})")
    
    st.write("Searching knowledge base...")
    chunks = search_kb(query, intent['space'])
    st.write(f"✓ Found {len(chunks)} relevant chunks")
    
    st.write("Generating response...")
    response = generate_response(query, chunks)
    status.update(label="Complete!", state="complete")
```

### API Integration

Uses existing query orchestrator:
```python
response = requests.post(
    f"{API_URL}/api/v1/queries/ask",
    json={
        "query": user_input,
        "frontend": "dashboard",
        "user_id": st.session_state.get("user_id", "anonymous")
    }
)
```

## Open Questions

1. **Thinking steps UI:** Show in real-time (streaming) or after complete? Real-time requires WebSocket or SSE.
2. **Feedback storage:** Log to database for analytics or just session-only?
3. **Welcome message:** Show instructions or example queries on first load?
4. **Clear chat confirmation:** Confirm before clearing or just clear immediately?

## Dependencies

No new dependencies - uses existing:
- streamlit (already in dashboard)
- requests (already used)

## Success Criteria

- [ ] Chat page accessible at `/Chat` in dashboard
- [ ] User can type and send queries
- [ ] Responses show with source citations
- [ ] Thinking steps visible (if enabled)
- [ ] Feedback buttons functional (session-only)
- [ ] Clear chat button works
- [ ] Chat history persists within session (page navigation)
- [ ] Responsive layout (doesn't break on mobile)

## Next Steps

→ `/ce:plan` for implementation details
