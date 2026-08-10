import re
from langchain_core.tools import tool
from db_utils import get_schema, run_query

# Forbidden SQL keywords that mutate or destroy data
FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]

@tool
def get_db_schema() -> str:
    """
    Returns the database schema showing all tables, columns, and data types.
    Always run this tool FIRST before writing a SQL query to know what tables and columns exist.
    """
    return get_schema()


@tool
def execute_sql_query(sql_query: str) -> str:
    """
    Executes a SELECT SQL query against the database and returns raw results.
    Input must be a valid, read-only SQL string.
    """
    # 1. Clean query string
    clean_query = sql_query.strip().upper()

    # 2. Enforce READ-ONLY restriction
    if not clean_query.startswith("SELECT"):
        return "SECURITY ERROR: Only read-only SELECT queries are allowed."

    # 3. Check for destructive keywords
    for keyword in FORBIDDEN_KEYWORDS:
        # Use regex word boundaries to avoid matching column names like 'updated_at'
        if re.search(rf"\b{keyword}\b", clean_query):
            return f"SECURITY ERROR: Destructive command '{keyword}' detected and blocked."

    # 4. Safe execution
    results = run_query(sql_query)
    return str(results)

# Local sanity test block
if __name__ == "__main__":
    print("=== Testing Safety Guardrails ===")
    print("Valid Query Test:", execute_sql_query.invoke({"sql_query": "SELECT * FROM employees LIMIT 1;"}))
    print("Forbidden Query Test:", execute_sql_query.invoke({"sql_query": "DROP TABLE employees;"}))