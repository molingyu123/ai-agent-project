from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from core.tools.data_analyzer import DataAnalyzerTool  # Will be implemented

class DataAnalysisAgent:
    """数据分析代理 - 支持项目数据分析、报告生成、洞察提取"""
    
    def __init__(self, llm=None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.prompt = ChatPromptTemplate.from_template(
            """你是一个专业的数据分析师。
            基于以下数据和用户查询，提供深入分析和洞察。
            数据: {data}
            查询: {query}
            
            输出格式:
            1. 关键指标总结
            2. 趋势分析
            3. 潜在问题与机会
            4. 推荐行动
            """
        )
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    async def analyze(self, query: str, data_source: str = "legacy"):
        """执行数据分析"""
        # 从遗留系统或数据库获取数据
        analyzer_tool = DataAnalyzerTool()
        raw_data = analyzer_tool.fetch_data(data_source)
        
        df = pd.DataFrame(raw_data) if isinstance(raw_data, list) else raw_data
        data_summary = df.describe().to_string() if not df.empty else "No data"
        
        result = await self.chain.ainvoke({
            "data": data_summary,
            "query": query
        })
        return result

# For integration with LangGraph
def create_analysis_node():
    agent = DataAnalysisAgent()
    async def node(state):
        query = state.get("query", "分析项目数据")
        result = await agent.analyze(query)
        return {"analysis_result": result, "next": "supervisor"}
    return node
