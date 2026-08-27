import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

# Initialize local in-memory ChromaDB client
chroma_client = chromadb.Client()
embedding_fn = DefaultEmbeddingFunction()

# Create or get vector collection
schema_collection = chroma_client.get_or_create_collection(
    name="db_schema_index",
    embedding_function=embedding_fn
)

# Simulated enterprise schemas with rich business descriptions
ENTERPRISE_TABLES = [
    {
        "table_name": "employees",
        "description": "Stores internal corporate staff records, employee full names, assigned department names, and base compensation salary figures.",
        "schema": "Table 'employees': id (INTEGER PRIMARY KEY), name (TEXT), department (TEXT), salary (REAL)"
    },
    {
        "table_name": "sales",
        "description": "Tracks individual customer transactions, revenue generated, sale transaction amounts, transaction timestamps, and the associated employee identifier who closed the deal.",
        "schema": "Table 'sales': id (INTEGER PRIMARY KEY), employee_id (INTEGER FOREIGN KEY), amount (REAL), sale_date (TEXT)"
    },
    {
        "table_name": "inventory_warehouse",
        "description": "Tracks physical warehouse inventory levels, product SKU numbers, stock quantities on shelves, and storage bin locations.",
        "schema": "Table 'inventory_warehouse': sku (TEXT PRIMARY KEY), warehouse_id (INTEGER), quantity_on_hand (INTEGER), aisle_number (INTEGER)"
    },
    {
        "table_name": "customer_support_tickets",
        "description": "Logs customer service tickets, issue complaint descriptions, escalation priority levels, resolution statuses, and assigned support reps.",
        "schema": "Table 'customer_support_tickets': ticket_id (INTEGER PRIMARY KEY), customer_id (INTEGER), priority_level (TEXT), status (TEXT), created_at (TEXT)"
    },
    {
        "table_name": "server_audit_logs",
        "description": "Security logs capturing user IP addresses, network port requests, authentication failure attempts, and API endpoint access timestamps.",
        "schema": "Table 'server_audit_logs': log_id (INTEGER PRIMARY KEY), client_ip (TEXT), endpoint (TEXT), status_code (INTEGER), access_time (TEXT)"
    }
]

def index_all_schemas():
    """Populates ChromaDB vector collection with table metadata embeddings."""
    ids = []
    documents = []
    metadatas = []

    for item in ENTERPRISE_TABLES:
        ids.append(item["table_name"])
        # Embed table name + business description for high semantic recall
        documents.append(f"Table: {item['table_name']}. Description: {item['description']}")
        metadatas.append({"table_name": item["table_name"], "schema": item["schema"]})

    schema_collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

# Pre-populate the index on module load
index_all_schemas()

def retrieve_relevant_schema(query: str, top_k: int = 2) -> str:
    """
    Performs semantic vector search over table schemas using ChromaDB.
    Returns only the top_k most relevant table schemas for the given user prompt.
    """
    results = schema_collection.query(
        query_texts=[query],
        n_results=top_k
    )

    retrieved_schemas = []
    if results and "metadatas" in results and results["metadatas"]:
        for match in results["metadatas"][0]:
            retrieved_schemas.append(match["schema"])

    return "\n".join(retrieved_schemas)


if __name__ == "__main__":
    print("=== Testing Vector Schema Indexing with ChromaDB ===")
    
    test_queries = [
        "Which employee closed the highest revenue deal?",
        "How many items are left in the warehouse shelves?",
        "Show suspicious IP addresses with failed logins."
    ]

    for q in test_queries:
        print(f"\nUser Query: '{q}'")
        matched = retrieve_relevant_schema(q, top_k=2)
        print("Retrieved Schemas via Vector Search:\n", matched)