"""Web UI with a code editor and chat, backed by the local model in main.py."""

import argparse
import sys

try:
    import gradio as gr
except ImportError:
    print('\nMissing gradio for the code editor UI.')
    print('Install with:  python -m pip install -r requirements.txt')
    sys.exit(1)

from main import (
    MODEL_NAME,
    build_context,
    generate_answer,
    load_knowledge,
    load_model,
    summarize_knowledge,
)


def create_ui(tokenizer, model):
    knowledge = load_knowledge()

    def respond(message, code, chat_history, history_state):
        if not message.strip():
            return chat_history, '', history_state

        question = message.strip()
        if code and code.strip():
            question = f'{question}\n\nCurrent code:\n```python\n{code.strip()}\n```'

        knowledge_context = ''
        if knowledge:
            knowledge_context = summarize_knowledge(knowledge, question)

        prompt = build_context(history_state, question)
        if knowledge_context:
            prompt += '\n\nRelevant knowledge:\n' + knowledge_context + '\nAssistant: '

        answer = generate_answer(tokenizer, model, prompt)
        chat_history = chat_history + [(message.strip(), answer)]
        history_state = history_state + [(question, answer)]
        return chat_history, '', history_state

    def clear_chat():
        return [], [], ''

    with gr.Blocks(title='AI Assistant + Code Editor') as demo:
        gr.Markdown('# Local AI Assistant — Code Editor')
        gr.Markdown('Write code on the left, ask questions on the right. Opens at http://127.0.0.1:7860')

        history = gr.State([])

        with gr.Row():
            code_editor = gr.Code(
                label='Code editor',
                language='python',
                lines=24,
                value='# Write Python here\n',
            )
            with gr.Column():
                chatbot = gr.Chatbot(label='Chat', height=420)
                msg = gr.Textbox(
                    label='Question',
                    placeholder='Explain this code, find bugs, suggest improvements…',
                )
                with gr.Row():
                    send = gr.Button('Send', variant='primary')
                    clear = gr.Button('Clear chat')

        inputs = [msg, code_editor, chatbot, history]
        outputs = [chatbot, msg, history]
        send.click(respond, inputs, outputs)
        msg.submit(respond, inputs, outputs)
        clear.click(clear_chat, outputs=[chatbot, history, msg])

    return demo


def launch(model_name: str, server_port: int = 7860):
    tokenizer, model = load_model(model_name)
    demo = create_ui(tokenizer, model)
    demo.launch(server_port=server_port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AI assistant with code editor UI.')
    parser.add_argument('--model', default=None, help='Model name or path')
    parser.add_argument('--port', type=int, default=7860, help='Port for the web UI')
    args = parser.parse_args()
    launch(args.model or MODEL_NAME, args.port)
