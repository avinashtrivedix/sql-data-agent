import sqlglot
from sqlglot import exp
from langchain_core.tools import tool
from db_utils import run_query
from schema_indexer import retrieve_relevant_schema

# Node types that alter, insert, or destroy database data
MUTATION_NODES = (
    exp.Drop,
    exp.Delete,
    exp.Insert,
    exp.Update,
    exp.Alter,
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
        if not isinstance(statement, exp.Select):
            return False, f"Non-read-only root statement detected: {statement.key.upper()}."

        for node in statement.walk():
            if isinstance(node, MUTATION_NODES):
                return False, f"Destructive operation '{node.key.upper()}' detected in AST node."

    return True, "Valid read-only query."


@tool
def get_db_schema(query: str) -> str:
    """
    Retrieves the most semantically relevant table schemas from the database using vector search.
    Always pass the user's natural language question into this tool before writing a SQL query.
    """
    return retrieve_relevant_schema(query, top_k=2)


@tool
def execute_sql_query(sql_query: str) -> str:
    """
    Executes a read-only SELECT SQL query against the database and returns raw results.
    Input must be a valid SQL string verified by AST validation.
    """
    is_valid, validation_msg = validate_readonly_ast(sql_query)
    if not is_valid:
        return f"SECURITY ERROR: {validation_msg}"

    results = run_query(sql_query)
    return str(results)