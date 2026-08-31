import streamlit as st
import pandas as pd
from agent import run_agent

# 1. Page Configuration
st.set_page_config(page_title="SQL Agent", page_icon="🤖", layout="centered")
st.title("Enterprise SQL Data Agent")
st.markdown("Ask natural language questions. The agent retrieves schemas, generates AST-validated SQL, and auto-corrects execution errors.")

# 2. Chat Interface State Management
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display previous chat messages
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. User Input
user_input = st.chat_input("E.g., What is the total sum of all sales?")

if user_input:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 4. Agent Execution with UI Spinners
    with st.chat_message("assistant"):
        with st.spinner("Analyzing schema and generating SQL..."):
            # Call our production agent engine
            agent_response = run_agent(user_input)
            
            if agent_response["status"] == "success":
                # Display Security/Attempt Badge
                st.success(f"✅ Executed safely in {agent_response['attempts']} attempt(s)")
                
                # Expandable Debug View for Technical Review
                with st.expander("🔍 View System Diagnostics"):
                    st.markdown("**Retrieved Schema (Vector Search):**")
                    st.code(agent_response["schema"], language="text")
                    st.markdown("**Executed SQL (AST Validated):**")
                    st.code(agent_response["sql"], language="sql")
                
                # Format Database Tuples into a Clean DataFrame
                raw_data = agent_response["result"]
                if raw_data:
                    df = pd.DataFrame(raw_data)
                    st.dataframe(df, use_container_width=True)
                    st.session_state.chat_history.append({"role": "assistant", "content": f"Found {len(raw_data)} records."})
                else:
                    st.info("Query executed successfully but returned no data.")
                    st.session_state.chat_history.append({"role": "assistant", "content": "No data returned."})
                    
            else:
                st.error("❌ Agent failed to generate a valid query.")
                st.code(agent_response["result"], language="text")
                st.session_state.chat_history.append({"role": "assistant", "content": "Failed to process query."})