import operator
from typing import Annotated, Any, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agents.analyzer import create_analysis_node
from agents.supervisor import SupervisorAgent
from core.tools.legacy_adapter import LegacyAdapter
from knowledge_base.retriever import KnowledgeRetriever


class AgentState(TypedDict, total=False):
    """Shared LangGraph state."""

    messages: Annotated[list[Any], operator.add]
    query: str
    analysis_result: str
    legacy_data: dict
    next: str
    final_answer: str


class MainWorkflow:
    """Main LangGraph workflow for routing specialist agents."""

    def __init__(self):
        self.legacy_adapter = LegacyAdapter()
        self.retriever = KnowledgeRetriever()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(state_schema=AgentState)

        workflow.add_node("supervisor", SupervisorAgent().route)
        workflow.add_node("analyzer", create_analysis_node())
        workflow.add_node("retriever", self._retrieve_node)
        workflow.add_node("legacy_sync", self._legacy_sync_node)

        workflow.add_conditional_edges(
            "supervisor",
            lambda state: state["next"],
            {
                "analyzer": "analyzer",
                "retriever": "retriever",
                "legacy": "legacy_sync",
                "end": END,
            },
        )

        workflow.add_edge("analyzer", END)
        workflow.add_edge("retriever", END)
        workflow.add_edge("legacy_sync", END)
        workflow.add_edge(START, "supervisor")

        return workflow.compile(checkpointer=MemorySaver())

    async def _retrieve_node(self, state: AgentState):
        result = self.retriever.query(state["query"])
        return {
            "messages": [{"role": "assistant", "content": result["answer"]}],
            "final_answer": result["answer"],
        }

    async def _legacy_sync_node(self, state: AgentState):
        data = self.legacy_adapter.sync_data()
        return {"legacy_data": data, "final_answer": f"Legacy sync result: {data}"}

    async def invoke(self, query: str, thread_id: str = "default"):
        config = {"configurable": {"thread_id": thread_id}}
        return await self.graph.ainvoke({"query": query, "messages": []}, config)


main_workflow = MainWorkflow()
