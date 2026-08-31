import sqlite3
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

chroma_client = chromadb.Client()
embedding_fn = DefaultEmbeddingFunction()
schema_collection = chroma_client.get_or_create_collection(
    name="live_db_schema",
    embedding_function=embedding_fn
)

def index_live_database(db_path: str = "data.db"):
    """Reads tables AND sample data dynamically to prevent LLM hallucinations."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    ids = []
    documents = []
    metadatas = []

    for table in tables:
        # 1. Get column definitions
        cursor.execute(f"PRAGMA table_info('{table}');")
        columns = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
        
        # 2. Get 2 rows of sample data (NEW)
        try:
            cursor.execute(f"SELECT * FROM {table} LIMIT 2;")
            sample_rows = cursor.fetchall()
            sample_text = f"Sample Data: {sample_rows}"
        except Exception:
            sample_text = "Sample Data: None"

        # 3. Combine schema and sample data for the LLM to read
        schema_text = f"Table '{table}': {', '.join(columns)}\n{sample_text}"

        ids.append(table)
        documents.append(f"Table name: {table}. Schema definition: {schema_text}")
        metadatas.append({"table_name": table, "schema": schema_text})

    conn.close()

    if ids:
        schema_collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

# Index on startup
index_live_database()

def retrieve_relevant_schema(query: str, top_k: int = 2) -> str:
    results = schema_collection.query(query_texts=[query], n_results=top_k)
    retrieved = []
    if results and "metadatas" in results and results["metadatas"]:
        for match in results["metadatas"][0]:
            retrieved.append(match["schema"])
    return "\n\n".join(retrieved)


if __name__ == "__main__":
    print("=== Testing Augmented Schema Indexer ===")
    user_q = "employee 1 sales"
    print(retrieve_relevant_schema(user_q, top_k=2))