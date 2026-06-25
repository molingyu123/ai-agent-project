from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage
import operator

from agents.supervisor import SupervisorAgent  # Will be created
from agents.analyzer import create_analysis_node
from knowledge_base.retriever import Retriever
from core.tools.legacy_adapter import LegacyAdapter

class AgentState(TypedDict):
    """LangGraph 主状态"""
    messages: Annotated[list[BaseMessage], operator.add]
    query: str
    analysis_result: str
    legacy_data: dict
    next: str

class MainWorkflow:
    """完整 LangGraph 主流程 - 集成所有功能"""
    
    def __init__(self):
        self.legacy_adapter = LegacyAdapter()
        self.retriever = Retriever()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(state_schema=AgentState)
        
        # 添加节点
        workflow.add_node("supervisor", SupervisorAgent().route)
        workflow.add_node("analyzer", create_analysis_node())
        workflow.add_node("retriever", self._retrieve_node)
        workflow.add_node("legacy_sync", self._legacy_sync_node)
        
        # 条件路由
        workflow.add_conditional_edges(
            "supervisor",
            lambda x: x["next"],
            {
                "analyzer": "analyzer",
                "retriever": "retriever",
                "legacy": "legacy_sync",
                "end": END
            }
        )
        
        workflow.add_edge("analyzer", "supervisor")
        workflow.add_edge("retriever", "supervisor")
        workflow.add_edge("legacy_sync", "supervisor")
        
        workflow.add_edge(START, "supervisor")
        
        return workflow.compile(checkpointer=MemorySaver())
    
    async def _retrieve_node(self, state: AgentState):
        """知识问答节点"""
        docs = await self.retriever.retrieve(state["query"])
        return {"messages": [f"Retrieved: {docs}"]}
    
    async def _legacy_sync_node(self, state: AgentState):
        """遗留系统同步节点"""
        data = self.legacy_adapter.sync_data()
        return {"legacy_data": data}
    
    async def invoke(self, query: str, thread_id: str = "default"):
        """主入口"""
        config = {"configurable": {"thread_id": thread_id}}
        return await self.graph.ainvoke({"query": query, "messages": []}, config)

# 初始化全局工作流
main_workflow = MainWorkflow()
