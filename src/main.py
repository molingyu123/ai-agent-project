import schedule
import time
import os
import yaml
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path

# RAG imports
try:
    import chromadb
    from chromadb.utils import embedding_functions
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("ChromaDB not installed, using placeholder RAG")

# Legacy system integration
def integrate_legacy_system():
    """对接原始老业务系统"""
    config = load_config()
    print(f"[{datetime.now()}] Integrating with legacy business system at {config['legacy_system']['api_endpoint']}...")
    try:
        # Example API call to legacy system
        response = requests.get(
            config['legacy_system']['api_endpoint'],
            headers={"Authorization": f"Bearer {config['legacy_system']['auth_token']}"},
            timeout=10
        )
        print(f"Legacy sync status: {response.status_code}")
    except Exception as e:
        print(f"Legacy integration error: {e}")

# Timed data listening
def monitor_data_updates():
    """定时监听更新数据"""
    config = load_config()
    print(f"[{datetime.now()}] Checking for data updates from sources...")
    # Example: Check file or DB updates
    for file_path in config.get('data_sources', {}).get('files', []):
        if Path(file_path['path']).exists():
            print(f"Detected update in: {file_path['path']}")
    # TODO: Add DB polling, webhooks

# Knowledge Q&A - Real RAG with ChromaDB
def knowledge_qa(query: str):
    """真实知识问答 - ChromaDB RAG实现"""
    print(f"[{datetime.now()}] Processing knowledge query: {query}")
    config = load_config()
    
    if not RAG_AVAILABLE:
        return f"基于知识库回答 '{query}'：ChromaDB未安装，使用占位响应。"
    
    try:
        # Initialize ChromaDB
        client = chromadb.PersistentClient(path="./knowledge_base/chroma_db")
        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=config['knowledge_base']['embedding_model']
        )
        
        # Create or get collection
        collection = client.get_or_create_collection(
            name="project_knowledge",
            embedding_function=embedding_func
        )
        
        # Load sample documents if empty
        if collection.count() == 0:
            with open("knowledge_base/sample_docs.txt", "r", encoding="utf-8") as f:
                docs = [line.strip() for line in f.readlines() if line.strip()]
            collection.add(
                documents=docs,
                ids=[f"doc_{i}" for i in range(len(docs))]
            )
            print("Loaded sample knowledge base.")
        
        # Query
        results = collection.query(
            query_texts=[query],
            n_results=2
        )
        
        context = "\n".join(results['documents'][0]) if results['documents'] else "No relevant docs."
        return f"基于知识库回答 '{query}'：\n{context}\n\n(真实RAG检索完成)"
    except Exception as e:
        print(f"RAG error: {e}")
        return f"RAG查询失败: {str(e)}"

# Data analysis
def analyze_project_data(data_source=None):
    """项目数据分析"""
    print(f"[{datetime.now()}] Analyzing project data...")
    try:
        # Example Pandas analysis
        df = pd.DataFrame({
            'project_id': [1, 2, 3],
            'value': [100, 200, 150],
            'date': pd.date_range(start='2026-01-01', periods=3)
        })
        insights = {
            'total': df['value'].sum(),
            'avg': df['value'].mean(),
            'trend': 'upward' if df['value'].diff().mean() > 0 else 'stable'
        }
        # Save report
        output_dir = Path(load_config()['analysis']['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_dir / 'analysis_report.xlsx', index=False)
        print(f"Report saved to {output_dir}/analysis_report.xlsx")
        return {"status": "analysis_complete", "insights": insights}
    except Exception as e:
        print(f"Analysis error: {e}")
        return {"status": "error"}

def load_config():
    """加载配置"""
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    print("🚀 Starting Production AI Agent System...")
    config = load_config()
    
    # Schedule tasks for production
    schedule.every(5).minutes.do(monitor_data_updates)
    schedule.every(30).minutes.do(integrate_legacy_system)  # More frequent for demo
    schedule.every(1).hour.do(lambda: analyze_project_data())
    
    # Demo one-time QA
    print(knowledge_qa("项目数据分析结果如何？"))
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()