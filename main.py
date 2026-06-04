"""
AI Assistant Framework

This script creates a local Python chatbot interface using Hugging Face models.
You can replace MODEL_NAME with a stronger model if you have the hardware.
"""

import argparse
import os
import sys
from pathlib import Path

MODEL_NAME = os.getenv('AI_MODEL', 'gpt2')
KNOWLEDGE_PATH = Path('knowledge_base.txt')

REQUIREMENTS = [
    'transformers>=4.35.0',
    'torch>=2.1.0',
    'sentence-transformers>=2.3.0',
]

SYSTEM_PROMPT = '''You are an advanced AI assistant designed to solve hard problems, explain complex ideas clearly, and generate Python code when needed. Answer thoroughly, step-by-step, and keep responses safe and precise.'''

CHAT_PROMPT_TEMPLATE = '''{system}

{history}

User: {question}
Assistant: '''


def print_install_instructions():
    print('\nMissing required Python packages for the assistant.')
    print('Install dependencies with:')
    print('  python -m pip install -r requirements.txt')
    print('\nIf you want a stronger model, set AI_MODEL to a larger checkpoint, e.g.:')
    print('  set AI_MODEL=tiiuae/falcon-7b-instruct')
    print('or on PowerShell:')
    print('  $env:AI_MODEL = \"tiiuae/falcon-7b-instruct\"')
    sys.exit(1)

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
    from sentence_transformers import SentenceTransformer
except ImportError:
    print_install_instructions()


def get_device():
    if torch.cuda.is_available():
        return 'cuda'
    if hasattr(torch, 'mps') and torch.backends.mps.is_available():
        return 'mps'
    return 'cpu'


def load_model(model_name: str):
    device = get_device()
    print(f'Loading model {model_name} on {device}...')
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)

    model_kwargs = {
        'torch_dtype': torch.float16 if device == 'cuda' else torch.float32,
        'low_cpu_mem_usage': True if device == 'cpu' else False,
    }
    if device == 'cuda':
        model_kwargs['device_map'] = 'auto'
    model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
    return tokenizer, model


def load_knowledge():
    if not KNOWLEDGE_PATH.exists():
        return []
    lines = [line.strip() for line in KNOWLEDGE_PATH.read_text(encoding='utf-8').splitlines() if line.strip()]
    return lines


def build_context(history, question):
    history_text = '\n'.join([f'User: {u}\nAssistant: {a}' for u, a in history[-6:]])
    return CHAT_PROMPT_TEMPLATE.format(system=SYSTEM_PROMPT, history=history_text, question=question)


def generate_answer(tokenizer, model, prompt: str):
    inputs = tokenizer(prompt, return_tensors='pt')
    if torch.cuda.is_available():
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

    generation_config = GenerationConfig(
        max_new_tokens=300,
        temperature=0.7,
        top_p=0.92,
        repetition_penalty=1.08,
        pad_token_id=tokenizer.eos_token_id or tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )

    outputs = model.generate(
        **inputs,
        generation_config=generation_config,
        do_sample=True,
        num_return_sequences=1,
        early_stopping=True,
    )
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text[len(prompt):].strip()


def chat_with_model(tokenizer, model, question, history=None):
    history = history or []
    if question is None or not question.strip():
        return ''

    knowledge = load_knowledge()
    knowledge_context = summarize_knowledge(knowledge, question) if knowledge else ''
    prompt = build_context(history, question)
    if knowledge_context:
        prompt += '\n\nRelevant knowledge:\n' + knowledge_context + '\nAssistant: '

    return generate_answer(tokenizer, model, prompt)


def summarize_knowledge(knowledge_list, query):
    if not knowledge_list:
        return ''

    embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    query_embedding = embedder.encode(query, normalize_embeddings=True)
    corpus_embeddings = embedder.encode(knowledge_list, normalize_embeddings=True)

    scores = [float(query_embedding.dot(item)) for item in corpus_embeddings]
    ranked = sorted(zip(scores, knowledge_list), reverse=True)
    top = [entry for _, entry in ranked[:3]]
    return '\n'.join(top)


def interactive_chat(tokenizer, model):
    history = []
    knowledge = load_knowledge()

    print('\n=== Local AI Chat Assistant ===')
    print('Type a question, or enter /exit to quit. Use /save to append a note to knowledge_base.txt.')

    while True:
        question = input('\nYou: ').strip()
        if not question:
            continue
        if question.lower() in ('/exit', '/quit'):
            print('Goodbye.')
            break
        if question.lower() == '/save':
            note = input('Knowledge note: ').strip()
            if note:
                with KNOWLEDGE_PATH.open('a', encoding='utf-8') as f:
                    f.write(note + '\n')
                knowledge.append(note)
                print('Saved to knowledge_base.txt.')
            continue

        knowledge_context = ''
        if knowledge:
            knowledge_context = summarize_knowledge(knowledge, question)
            if knowledge_context:
                print('\n[Using knowledge base to enrich the answer.]')

        prompt = build_context(history, question)
        if knowledge_context:
            prompt = prompt + '\n\nRelevant knowledge:\n' + knowledge_context + '\nAssistant: '

        answer = generate_answer(tokenizer, model, prompt)
        print('\nAssistant:', answer)
        history.append((question, answer))


def main():
    parser = argparse.ArgumentParser(description='Run a local Python AI assistant.')
    parser.add_argument('--model', help='Model name or path to use for the assistant')
    parser.add_argument('--ui', action='store_true', help='Open web UI with code editor')
    parser.add_argument('--port', type=int, default=7860, help='Port for --ui (default: 7860)')
    args = parser.parse_args()

    model_name = args.model or MODEL_NAME
    if args.ui:
        from editor_ui import launch

        launch(model_name, args.port)
        return

    tokenizer, model = load_model(model_name)
    interactive_chat(tokenizer, model)

from backend import app  # ← ENG YUQORIGA, boshqa import'lar yoniga

# ... qolgan kod ...

if __name__ == '__main__':
    main()