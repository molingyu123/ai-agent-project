from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

class SupervisorAgent:
    """监督代理 - 路由任务到对应专业代理"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.prompt = ChatPromptTemplate.from_template(
            """你是任务路由主管。根据用户查询决定下一步：
            查询: {query}
            
            选项:
            - analyzer: 数据分析相关
            - retriever: 知识问答
            - legacy: 需要同步老系统数据
            - end: 完成
            
            只返回一个选项名称。
            """
        )
        self.chain = self.prompt | self.llm | (lambda x: {"next": x.content.strip().lower()})
    
    def route(self, state):
        return self.chain.invoke({"query": state["query"]})
