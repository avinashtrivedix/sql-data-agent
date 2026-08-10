import sqlite3

DB_PATH = "data.db"

def get_schema() -> str:
    """
    Extracts the database schema (table names, column names, and data types).
    An LLM needs this exact string in its context to write valid SQL queries.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get names of all user-defined tables in the SQLite database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    schema_lines = []
    for table in tables:
        # PRAGMA table_info returns metadata: (cid, name, type, notnull, dflt_value, pk)
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        
        # Format columns as: column_name (DATA_TYPE)
        col_descriptions = [f"{col[1]} ({col[2]})" for col in columns]
        schema_lines.append(f"Table '{table}': {', '.join(col_descriptions)}")

    conn.close()
    return "\n".join(schema_lines)


def run_query(sql_query: str):
    """
    Executes a SQL query against the database and returns raw results or error messages.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        return results
    except sqlite3.Error as e:
        conn.close()
        return f"SQL Error: {str(e)}"


# Local sanity test block
if __name__ == "__main__":
    print("=== Testing Schema Extraction ===")
    print(get_schema())
    
    print("\n=== Testing Query Execution ===")
    test_query = "SELECT name, salary FROM employees WHERE department = 'Engineering';"
    print(f"Executing: {test_query}")
    print(f"Result: {run_query(test_query)}")