import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config.settings import settings

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Routes user intent to the right specialist agent."""

    VALID_ROUTES = {"analyzer", "retriever", "legacy", "end"}

    def __init__(self):
        self.chain = None
        if settings.openai_api_key:
            llm = ChatOpenAI(
                model=settings.chat_model,
                temperature=0,
                openai_api_key=settings.openai_api_key,
            )
            prompt = ChatPromptTemplate.from_template(
                """You are a task router for a production AI agent system.
Route the user query to exactly one option.

Options:
- analyzer: project metrics, trends, reports, statistics, operational analysis
- retriever: knowledge Q&A, policy lookup, document search, RAG
- legacy: sync, import, connector, legacy system, old system data integration
- end: no action needed

Query: {query}

Return only one option name."""
            )
            self.chain = prompt | llm

    def route(self, state):
        query = state.get("query", "")
        if self.chain is None:
            return {"next": self._heuristic_route(query)}

        try:
            response = self.chain.invoke({"query": query})
            route = response.content.strip().lower()
            return {"next": route if route in self.VALID_ROUTES else self._heuristic_route(query)}
        except Exception:
            logger.exception("LLM routing failed; falling back to heuristic routing.")
            return {"next": self._heuristic_route(query)}

    def _heuristic_route(self, query: str) -> str:
        normalized = query.lower()
        legacy_terms = ["sync", "import", "legacy", "connector", "old system", "同步", "导入", "遗留", "老系统", "对接"]
        analysis_terms = ["analysis", "analyze", "report", "trend", "metric", "统计", "分析", "报表", "趋势", "指标"]
        rag_terms = ["knowledge", "document", "policy", "question", "rag", "知识", "文档", "制度", "问答"]

        if any(term in normalized for term in legacy_terms):
            return "legacy"
        if any(term in normalized for term in analysis_terms):
            return "analyzer"
        if any(term in normalized for term in rag_terms):
            return "retriever"
        return "retriever"
