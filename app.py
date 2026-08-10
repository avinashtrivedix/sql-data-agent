import streamlit as st
from agent import agent_executor
from db_utils import get_schema

st.set_page_config(page_title="SQL Data Agent", page_icon="📊", layout="wide")

st.title("📊 Autonomous SQL Data Agent")
st.caption("Ask questions about your database in natural language.")

# Sidebar: Live Database Schema Viewer
with st.sidebar:
    st.header("🗄️ Database Schema")
    st.text(get_schema())

# Initialize session chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt input
if user_query := st.chat_input("e.g., Who earns the highest salary in Engineering?"):
    # Display user input
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Process query with agent
    with st.chat_message("assistant"):
        with st.status("Agent thinking & running SQL...", expanded=True) as status:
            try:
                response = agent_executor.invoke({"messages": [("user", user_query)]})
                
                # Render intermediate tool execution steps inside the status box
                for msg in response["messages"]:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        tool_name = msg.tool_calls[0]["name"]
                        st.write(f"🛠️ **Tool Used:** `{tool_name}`")
                        if "sql_query" in msg.tool_calls[0]["args"]:
                            st.code(msg.tool_calls[0]["args"]["sql_query"], language="sql")
                    elif msg.type == "tool":
                        st.write(f"📥 **Raw DB Output:** `{msg.content}`")

                final_answer = response["messages"][-1].content
                status.update(label="Query Execution Complete!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Execution Error", state="error")
                final_answer = f"Error processing query: {str(e)}"

        # Display final text answer
        st.markdown(final_answer)
        st.session_state.messages.append({"role": "assistant", "content": final_answer})