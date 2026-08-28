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
    """Reads all real tables dynamically from SQLite and indexes them into ChromaDB."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    ids = []
    documents = []
    metadatas = []

    for table in tables:
        cursor.execute(f"PRAGMA table_info('{table}');")
        columns = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
        schema_text = f"Table '{table}': {', '.join(columns)}"

        ids.append(table)
        documents.append(f"Table name: {table}. Schema definition: {schema_text}")
        metadatas.append({"table_name": table, "schema": schema_text})

    conn.close()

    if ids:
        schema_collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

# Index actual data.db file on startup
index_live_database()

def retrieve_relevant_schema(query: str, top_k: int = 2) -> str:
    """Finds the most relevant real table schemas from data.db based on semantic similarity."""
    results = schema_collection.query(query_texts=[query], n_results=top_k)
    
    retrieved = []
    if results and "metadatas" in results and results["metadatas"]:
        for match in results["metadatas"][0]:
            retrieved.append(match["schema"])
    return "\n".join(retrieved)


if __name__ == "__main__":
    print("=== Testing Live Database Schema Retrieval ===")
    user_q = "What is the highest salary paid?"
    print(f"Query: '{user_q}'")
    print(retrieve_relevant_schema(user_q, top_k=1))