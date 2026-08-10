from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from tools import get_db_schema, execute_sql_query

# 1. Initialize local LLM engine
llm = ChatOllama(model="qwen2.5", temperature=0)

# 2. Register tools
tools = [get_db_schema, execute_sql_query]

# 3. Guardrailed System Prompt
SYSTEM_PROMPT = """You are a SQL Data Analyst assistant connected to a SQLite database.

CRITICAL WORKFLOW & QUOTING RULES:
1. Always call 'get_db_schema' FIRST to inspect table names and columns.
2. Inside your SQL queries, ALWAYS use SINGLE QUOTES for string literals (e.g. WHERE department = 'Engineering'). NEVER use double quotes inside SQL.
3. Call 'execute_sql_query' immediately to run the query.
4. Summarize the returned results.

Valid SQL Example:
SELECT name, salary FROM employees WHERE department = 'Engineering' ORDER BY salary DESC LIMIT 1;
"""

# 4. Create agent graph
agent_executor = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT
)

if __name__ == "__main__":
    user_query = "Which employee has the highest total sales volume, and what is their name?"
    print(f"User Question: {user_query}\n")
    print("--- Full Agent Execution Trace ---")

    response = agent_executor.invoke({"messages": [("user", user_query)]})

    for i, msg in enumerate(response["messages"]):
        role = msg.type.upper()
        print(f"\n[Step {i+1} - {role}]:")
        
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"Tool Invoked: {msg.tool_calls[0]['name']}")
            print(f"Arguments: {msg.tool_calls[0]['args']}")
        else:
            print(msg.content)