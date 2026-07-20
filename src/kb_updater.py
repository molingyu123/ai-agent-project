import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import chromadb
from chromadb.utils import embedding_functions
import yaml

def load_config():
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class KBUpdateHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(('.txt', '.md', '.sql')):
            print(f"🔄 Detected change in {event.src_path}, updating knowledge base...")
            update_knowledge_base()

def update_knowledge_base():
    """自动更新知识库"""
    config = load_config()
    try:
        client = chromadb.PersistentClient(path="./knowledge_base/chroma_db")
        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=config['knowledge_base']['embedding_model']
        )
        collection = client.get_or_create_collection(
            name="project_knowledge",
            embedding_function=embedding_func
        )
        
        # Re-load all docs
        docs = []
        doc_ids = []
        for doc_file in ["sample_docs.txt", "business_docs.md", "business_schema.sql", "multimodal_note.txt"]:
            try:
                with open(f"knowledge_base/{doc_file}", "r", encoding="utf-8") as f:
                    content = f.read()
                    chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
                    docs.extend(chunks)
                    doc_ids.extend([f"{doc_file}_{i}" for i in range(len(chunks))])
            except FileNotFoundError:
                pass
        
        if docs:
            collection.delete(ids=doc_ids)  # Clear old
            collection.add(documents=docs, ids=doc_ids)
            print(f"✅ Knowledge base updated with {len(docs)} chunks.")
    except Exception as e:
        print(f"Update error: {e}")

if __name__ == "__main__":
    update_knowledge_base()