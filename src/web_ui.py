import gradio as gr
from main import knowledge_qa, analyze_project_data
import threading
import time

def chat_interface(message, history):
    response = knowledge_qa(message)
    return response

def launch_ui():
    with gr.Blocks(title="AI智能体 - 生产业务对话系统") as demo:
        gr.Markdown("# 🚀 生产级AI智能体对话界面\n对接老系统 + 实时知识问答 + 数据分析")
        
        with gr.Tab("知识对话"):
            chatbot = gr.Chatbot()
            msg = gr.Textbox(label="输入业务问题")
            clear = gr.Button("清空")
            
            def respond(message, chat_history):
                bot_message = knowledge_qa(message)
                chat_history.append((message, bot_message))
                return "", chat_history
            
            msg.submit(respond, [msg, chatbot], [msg, chatbot])
            clear.click(lambda: None, None, chatbot, queue=False)
        
        with gr.Tab("数据分析"):
            analyze_btn = gr.Button("执行项目数据分析")
            output = gr.Textbox(label="分析结果")
            analyze_btn.click(lambda: str(analyze_project_data()), None, output)
        
        gr.Markdown("知识库自动更新已启用 - 修改knowledge_base文件即可实时生效")
    
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    # Start KB watcher in background
    from kb_updater import update_knowledge_base
    update_knowledge_base()  # Initial
    print("Web UI starting at http://localhost:7860")
    launch_ui()