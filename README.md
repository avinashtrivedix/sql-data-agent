# Autonomous Text-to-SQL Data Agent

An enterprise-grade Text-to-SQL AI agent built with **LangChain**, **ChromaDB**, and **SQLGlot**. Translates natural language into optimized relational SQL queries with AST-based security validation, semantic vector schema retrieval, and deterministic execution.

## Architecture
User Query ──► ChromaDB Vector Retrieval ──► Top-K Relevant Schemas
│
▼
Llama 3.2 (Local via Ollama)
│
▼
SQLGlot AST Validation ──► [Blocks DROP / Mutations]
│
▼
SQLite Engine (Safe Execution) ──► Structured Output

## Key Engineering Features

- **AST Query Validation (`SQLGlot`):** Replaces brittle regex matching with Abstract Syntax Tree parsing to guarantee strictly read-only `SELECT` queries and prevent subquery injection attacks.
- **Dynamic Vector Schema Indexing (`ChromaDB`):** Performs semantic cosine similarity search over table metadata, dynamically injecting only relevant table schemas into the context window to eliminate prompt bloat and column hallucinations.
- **Deterministic SLM Execution Pipeline:** Formats schema context directly for lightweight local models (Llama 3.2), avoiding function-calling dropouts while maintaining low memory overhead.
- **Automated Benchmark Evaluation Suite:** Evaluates performance against standard Text-to-SQL metrics (Execution Accuracy & AST Safety).

