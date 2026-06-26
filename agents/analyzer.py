from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config.settings import settings
from core.tools.data_analyzer import DataAnalyzerTool


class DataAnalysisAgent:
    """Project data analysis agent."""

    def __init__(self, llm=None):
        self.tool = DataAnalyzerTool()
        self.chain = None
        if llm is not None:
            self.chain = self._build_chain(llm)
        elif settings.openai_api_key:
            self.chain = self._build_chain(
                ChatOpenAI(
                    model=settings.chat_model,
                    temperature=0,
                    openai_api_key=settings.openai_api_key,
                )
            )

    def _build_chain(self, llm):
        prompt = ChatPromptTemplate.from_template(
            """You are a senior data analyst for a production AI agent platform.
Use the provided data summary to answer the user's request.

Data summary:
{data}

User request:
{query}

Return:
1. Key metrics
2. Trend or anomaly assessment
3. Risks and opportunities
4. Recommended actions"""
        )
        return prompt | llm | StrOutputParser()

    async def analyze(self, query: str, data_source: str = "sync_jobs"):
        data = self.tool.fetch_data(data_source)
        data_summary = self.tool.summarize(data)

        if self.chain is None:
            return data_summary

        return await self.chain.ainvoke({"data": data_summary, "query": query})


def create_analysis_node():
    agent = DataAnalysisAgent()

    async def node(state):
        query = state.get("query", "Analyze project data")
        result = await agent.analyze(query)
        return {"analysis_result": result, "final_answer": result}

    return node
