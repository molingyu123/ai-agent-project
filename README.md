# AI Agent Project

Production-oriented AI agent scaffold for legacy system integration, scheduled data sync, RAG knowledge Q&A, and project data analysis.

## Architecture

- FastAPI for service APIs
- LangGraph for agent orchestration
- PostgreSQL for business data, agent state metadata, sync jobs, and reports
- pgvector for the default RAG vector store
- Redis + Celery for scheduled and asynchronous jobs

## Database Strategy

This project uses PostgreSQL as the system of record and pgvector as the first vector-search implementation.

Use this setup first when the project needs strong metadata filtering, transactions, backups, permissions, and simpler operations. Keep the vector-store boundary abstract so the system can later move high-scale vector search to Zvec, DashVector, Qdrant, Milvus, OpenSearch, or another dedicated engine.

## Quick Start

1. Copy environment variables:

   ```bash
   cp .env.example .env
   ```

2. Start services:

   ```bash
   docker compose up -d --build
   ```

3. Open the API:

   ```text
   http://localhost:8000/docs
   ```

## Main Endpoints

- `POST /chat/query` - RAG Q&A
- `POST /agent/invoke` - LangGraph agent entrypoint
- `POST /knowledge/index-text` - index text into the knowledge base
- `POST /sync/legacy` - sync API, DB, or file-based legacy data
- `GET /health` - API health check

## Production Notes

Before real deployment, add authentication, tenant/project permission checks, migrations, persistent LangGraph checkpoints, observability, prompt/version governance, RAG evaluation datasets, and connector-specific retry/idempotency rules.
