# Production AI Agent Architecture

## Positioning

The system is designed for four business capabilities:

- Legacy system integration through controlled connectors
- Scheduled data synchronization into a normalized data layer
- RAG-based knowledge Q&A with source metadata
- Project data analysis and report generation

## Recommended Data Architecture

PostgreSQL is the system of record. It stores users, sessions, sync jobs, connector metadata, project data, reports, tool calls, and audit records.

pgvector is the default vector-search implementation. It is suitable for early production because metadata and vectors can be managed in the same operational database.

Dedicated vector stores should be introduced behind the vector-store interface when scale or retrieval requirements exceed what one PostgreSQL cluster should carry. Typical triggers include very large vector collections, high write throughput, strict multi-tenant isolation, GPU or distributed ANN indexing needs, or complex hybrid search.

## Agent Layer

LangGraph routes requests to specialist agents:

- Supervisor: classifies intent and selects the next node
- Retriever: performs RAG retrieval and answer generation
- Analyzer: reads controlled data summaries and generates analysis
- Legacy Sync: imports data from external systems through adapters

All external access should go through tool classes. The model should not directly access databases, files, or HTTP endpoints.

## Sync Pipeline

The target pipeline is:

1. Connector extracts data from API, DB, or files.
2. A sync job records status, counts, errors, and metadata.
3. Raw records are normalized into business tables.
4. Textual records are chunked and embedded.
5. Embeddings are written to the vector store with source metadata.
6. RAG answers cite source metadata.

## Scale Notes On Alibaba Vector Products

Alibaba has public materials for large-scale vector retrieval. Zvec is an open-source embedded vector search library that describes billion-scale retrieval capability, while Alibaba Cloud products such as DashVector/OpenSearch also target large vector-search workloads.

That does not make a vector database a replacement for PostgreSQL. Vector engines solve similarity retrieval; PostgreSQL still owns transactions, metadata, permissions, auditability, normalized business records, and operational reporting. Keep the storage boundary abstract so large deployments can switch the vector backend without rewriting the agent and business layers.
