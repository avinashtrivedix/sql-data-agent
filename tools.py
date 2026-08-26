import sqlglot
from sqlglot import exp
from langchain_core.tools import tool
from db_utils import get_schema, run_query

# Node types that alter, insert, or destroy database data
MUTATION_NODES = (
    exp.Drop,
    exp.Delete,
    exp.Insert,
    exp.Update,
    exp.AlterTable,
    exp.Create,
    exp.Command,
)

def validate_readonly_ast(sql_query: str) -> tuple[bool, str]:
    """
    Parses a SQL string into an Abstract Syntax Tree (AST) using SQLGlot.
    Validates that:
      1. The query contains valid SQL syntax.
      2. All parsed statements are strictly SELECT statements.
      3. No mutation nodes exist in any subtrees or subqueries.
    """
    try:
        parsed_statements = sqlglot.parse(sql_query)
    except Exception as err:
        return False, f"SQL Syntax Parsing Error: {str(err)}"

    if not parsed_statements or parsed_statements == [None]:
        return False, "Empty or unparseable SQL statement."

    for statement in parsed_statements:
        # Check root expression
        if not isinstance(statement, exp.Select):
            return False, f"Non-read-only root statement detected: {statement.key.upper()}."

        # Walk entire expression tree to catch subquery mutations or injections
        for node in statement.walk():
            if isinstance(node, MUTATION_NODES):
                return False, f"Destructive operation '{node.key.upper()}' detected in AST node."

    return True, "Valid read-only query."


@tool
def get_db_schema() -> str:
    """
    Returns the database schema showing all tables, columns, and data types.
    Always run this tool FIRST before writing a SQL query.
    """
    return get_schema()


@tool
def execute_sql_query(sql_query: str) -> str:
    """
    Executes a read-only SELECT SQL query against the database and returns raw results.
    Input must be a valid SQL string verified by AST validation.
    """
    # 1. AST Security Validation
    is_valid, validation_msg = validate_readonly_ast(sql_query)
    if not is_valid:
        return f"SECURITY ERROR: {validation_msg}"

    # 2. Safe Execution
    results = run_query(sql_query)
    return str(results)


if __name__ == "__main__":
    print("=== Testing AST Security Guardrails ===")
    
    # Test 1: Valid SELECT
    test1 = "SELECT name, salary FROM employees WHERE salary > 50000;"
    print("1. Valid Query:", execute_sql_query.invoke({"sql_query": test1}))

    # Test 2: Destructive root command
    test2 = "DROP TABLE employees;"
    print("2. DROP Statement:", execute_sql_query.invoke({"sql_query": test2}))

    # Test 3: Tricky string containing mutation word (Regex often fails, AST passes)
    test3 = "SELECT * FROM employees WHERE department = 'DROP';"
    print("3. Valid string literal with 'DROP':", execute_sql_query.invoke({"sql_query": test3}))

    # Test 4: Chained injection attempt
    test4 = "SELECT * FROM employees; DROP TABLE sales;"
    print("4. Chained Injection:", execute_sql_query.invoke({"sql_query": test4}))