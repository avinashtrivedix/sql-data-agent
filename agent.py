import re
from langchain_ollama import ChatOllama
from schema_indexer import retrieve_relevant_schema
from tools import execute_sql_query

# 1. Initialize local lightweight LLM
llm = ChatOllama(model="llama3.2", temperature=0)

SQL_PROMPT_TEMPLATE = """You are a SQL Data Analyst. Write a single SQLite SELECT query to answer the user's question.

Relevant Database Schema:
{schema}

User Question: {question}

MANDATORY RULES:
1. Return ONLY the raw SQL query inside a ```sql ... ``` block.
2. Use ONLY the table and column names specified in the schema above.
3. The query MUST be a read-only SELECT statement.
"""

def run_agent(user_query: str) -> str:
    """
    Production-grade SLM pipeline:
    1. Semantically retrieves relevant schemas via ChromaDB.
    2. Directly conditions the LLM with the retrieved schema context.
    3. Extracts SQL, validates AST safety, and executes against SQLite.
    """
    # 1. Retrieve relevant schema using ChromaDB vector search
    retrieved_schema = retrieve_relevant_schema(user_query, top_k=2)
    
    # 2. Format prompt with schema context
    prompt = SQL_PROMPT_TEMPLATE.format(
        schema=retrieved_schema,
        question=user_query
    )
    
    # 3. Model generates the SQL query
    response = llm.invoke(prompt)
    raw_content = response.content
    
    # 4. Extract SQL from code block or raw text
    sql_match = re.search(r"```sql\s*(.*?)\s*```", raw_content, re.DOTALL | re.IGNORECASE)
    if sql_match:
        sql_query = sql_match.group(1).strip()
    else:
        # Fallback to single line/clean string if no markdown blocks used
        sql_query = raw_content.strip()

    # 5. Execute through our SQLGlot AST validation engine
    db_result = execute_sql_query.invoke({"sql_query": sql_query})
    
    return f"**Retrieved Schema:**\n```\n{retrieved_schema}\n```\n\n**Generated SQL:**\n```sql\n{sql_query}\n```\n\n**Result:**\n`{db_result}`"


if __name__ == "__main__":
    print("=== Testing Direct SLM Vector-Augmented Pipeline ===")
    test_query = "What is the total sum of all sales amounts?"
    
    output = run_agent(test_query)
    print("\n" + output)