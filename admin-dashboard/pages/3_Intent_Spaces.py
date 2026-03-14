"""Intent spaces configuration page"""
import os
import streamlit as st
import requests

st.title("🎯 Intent Spaces")

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.markdown("""
Intent spaces categorize your documents and queries into logical groups.
- **HR**: Human resources policies, employee handbook, benefits
- **Legal**: Contracts, compliance, legal documents
- **Finance**: Expense policies, financial procedures, budgets
- **General**: Uncategorized documents and general queries
""")

st.markdown("---")

st.header("Current Intent Spaces")

col1, col2, col3, col4 = st.columns(4)

intent_spaces = [
    {"name": "HR", "icon": "👥", "description": "Human Resources"},
    {"name": "Legal", "icon": "⚖️", "description": "Legal & Compliance"},
    {"name": "Finance", "icon": "💰", "description": "Finance & Expenses"},
    {"name": "General", "icon": "📋", "description": "General Knowledge"}
]

for col, space in zip([col1, col2, col3, col4], intent_spaces):
    with col:
        st.subheader(f"{space['icon']} {space['name']}")
        st.caption(space['description'])

st.markdown("---")

st.header("Intent Classification Keywords")

st.markdown("""
The system uses keywords to classify queries into intent spaces automatically.

**Current keyword patterns:**
- **HR**: employee, staff, hiring, recruitment, payroll, benefits, leave, vacation
- **Legal**: contract, agreement, terms, compliance, regulation, law, liability
- **Finance**: expense, budget, reimbursement, invoice, payment, accounting, tax
""")

st.info("💡 When a query matches keywords from multiple spaces, the system uses confidence scoring to choose the best match.")