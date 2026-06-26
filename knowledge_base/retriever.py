"""RAG retrieval service for knowledge Q&A."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from langchain_community.vectorstores import PGVector
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from config.settings import settings

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """Thin RAG facade with lazy vector-store initialization."""

    def __init__(self):
        self._embeddings: OpenAIEmbeddings | None = None
        self._vectorstore: PGVector | None = None

    @property
    def embeddings(self) -> OpenAIEmbeddings:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for embeddings.")
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openai_api_key,
            )
        return self._embeddings

    @property
    def vectorstore(self) -> PGVector:
        if settings.vector_store_provider != "pgvector":
            raise NotImplementedError(
                f"Vector store provider '{settings.vector_store_provider}' is not implemented yet."
            )
        if self._vectorstore is None:
            self._vectorstore = PGVector(
                connection_string=settings.postgres_url,
                embedding_function=self.embeddings,
                collection_name=settings.vector_collection_name,
            )
        return self._vectorstore

    def add_texts(self, texts: list[str], metadatas: list[dict[str, Any]] | None = None) -> list[str]:
        if not texts:
            return []
        return self.vectorstore.add_texts(texts=texts, metadatas=metadatas)

    def retrieve(self, question: str, k: int | None = None) -> list[Document]:
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": k or settings.vector_search_k}
        )
        if hasattr(retriever, "invoke"):
            return retriever.invoke(question)
        return retriever.get_relevant_documents(question)

    async def aretrieve(self, question: str, k: int | None = None) -> list[Document]:
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": k or settings.vector_search_k}
        )
        if hasattr(retriever, "ainvoke"):
            return await retriever.ainvoke(question)
        return self.retrieve(question, k=k)

    def get_qa_chain(self, llm):
        template = """You are a production AI agent. Answer only from the provided context.
If the answer is not in the context, say that the current knowledge base does not contain enough information.

Context:
{context}

Question: {question}
"""
        prompt = ChatPromptTemplate.from_template(template)
        return (
            {"context": self.retrieve, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    def query(self, question: str, llm=None) -> dict[str, Any]:
        try:
            docs = self.retrieve(question)
        except Exception as exc:
            logger.exception("RAG retrieval failed")
            return {
                "answer": "Knowledge retrieval is not available. Check database, pgvector, and embedding settings.",
                "sources": [],
                "error": str(exc),
            }

        if not docs:
            return {
                "answer": "The current knowledge base does not contain enough information.",
                "sources": [],
            }

        llm = llm or self._default_llm()
        if llm is None:
            return {
                "answer": self._extractive_answer(docs),
                "sources": self._format_sources(docs),
            }

        chain = self.get_qa_chain(llm)
        answer = chain.invoke(question)
        return {"answer": answer, "sources": self._format_sources(docs)}

    def _default_llm(self):
        if not settings.openai_api_key:
            return None
        return ChatOpenAI(
            model=settings.chat_model,
            temperature=0,
            openai_api_key=settings.openai_api_key,
        )

    def _extractive_answer(self, docs: list[Document]) -> str:
        snippets = [doc.page_content.strip()[:600] for doc in docs[:3] if doc.page_content.strip()]
        return "\n\n".join(snippets) if snippets else "No usable content was retrieved."

    def _format_sources(self, docs: list[Document]) -> list[dict[str, Any]]:
        return [
            {
                "content": doc.page_content[:300],
                "metadata": doc.metadata,
            }
            for doc in docs
        ]


@lru_cache(maxsize=1)
def get_retriever() -> KnowledgeRetriever:
    return KnowledgeRetriever()


retriever = get_retriever()
