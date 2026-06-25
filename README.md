# AI Agent Project

生产级 AI 智能体项目，支持遗留系统对接、定时数据同步、RAG 知识问答、项目数据分析。

## 架构
- LangGraph + LangChain
- PostgreSQL + PGVector
- Celery for scheduling
- FastAPI backend

## 快速开始
1. `cp .env.example .env`
2. `docker-compose up -d`
3. `poetry install` or `pip install -r requirements.txt`

See docs/architecture.md for details.