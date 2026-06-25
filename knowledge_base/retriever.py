"""
RAG Retriever for Knowledge Q&A.
"""

from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class KnowledgeRetriever:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        self.vectorstore = PGVector(
            connection_string=settings.postgres_url,
            embedding_function=self.embeddings,
            collection_name="knowledge_base"
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 6})
    
    def get_qa_chain(self, llm):
        """Build RAG chain"""
        template = """Answer the question based on the following context:
        {context}
        
        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        
        chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return chain
    
    def query(self, question: str, llm=None):
        """Simple query"""
        docs = self.retriever.get_relevant_documents(question)
        return {"answer": "Processed via RAG", "sources": [doc.page_content[:200] for doc in docs]}

retriever = KnowledgeRetriever()