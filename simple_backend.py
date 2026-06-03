"""Lightweight chat server with optional local Ollama and remote API support."""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import List

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

if load_dotenv is not None:
    load_dotenv()

OLLAMA_URL = 'http://127.0.0.1:11434'
OLLAMA_MODEL = 'mistral'
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('OPENAI_API_KEY')

app = FastAPI(title='AI Chat API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class ChatRequest(BaseModel):
    question: str
    history: List[List[str]] = []

class ChatResponse(BaseModel):
    answer: str
    history: List[List[str]]


def ollama_available() -> bool:
    try:
        req = urllib.request.Request(f'{OLLAMA_URL}/v1/models', method='GET')
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.load(resp)
            return isinstance(data, list) or isinstance(data, dict)
    except Exception:
        return False


def ask_ollama(question: str) -> str:
    payload = {
        'messages': [
            {'role': 'user', 'content': question},
        ]
    }
    req = urllib.request.Request(
        f'{OLLAMA_URL}/v1/chat/{OLLAMA_MODEL}',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)

    # Ollama response can contain different fields depending on version.
    if isinstance(data, dict):
        if 'choices' in data and data['choices']:
            choice = data['choices'][0]
            if isinstance(choice, dict):
                if 'message' in choice and isinstance(choice['message'], dict):
                    return choice['message'].get('content', '')
                if 'content' in choice:
                    return choice['content']
        if 'completion' in data:
            return data['completion']
    return str(data)


def ask_google_gemini(question: str) -> str:
    if not GOOGLE_API_KEY:
        raise RuntimeError('GOOGLE_API_KEY yoki OPENAI_API_KEY aniqlanmagan')

    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent'
    payload = {
        'contents': [
            {
                'parts': [
                    {'text': question}
                ]
            }
        ]
    }
    req_data = json.dumps(payload).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GOOGLE_API_KEY,
    }

    last_error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.load(resp)

            if isinstance(data, dict):
                if 'candidates' in data and data['candidates']:
                    candidate = data['candidates'][0]
                    if isinstance(candidate, dict) and 'content' in candidate:
                        content = candidate['content']
                        if isinstance(content, dict) and 'parts' in content and content['parts']:
                            return content['parts'][0].get('text', '')
                if 'output' in data:
                    return data['output']
            return str(data)
        except Exception as exc:
            last_error = exc
            import time
            time.sleep(2)
    raise last_error



def get_simple_response(question: str) -> str:
    question_lower = question.lower()

    if any(word in question_lower for word in ['salom', 'hello', 'hi', 'assalomu']):
        return 'Salom! Men AI assistentman. Savolingizni berasizmi?'

    if any(word in question_lower for word in ['ism', 'kim', 'who', 'nima']):
        return 'Men sizning AI assistentinizman. Men savollaringizga javob beraman va kodingizni yozishda yordam beraman.'

    if any(word in question_lower for word in ['python', 'kod', 'code']):
        return 'Python juda yaxshi til! Men Python kodu yozishda yordam beraman. Masalan, for loop yoki if statement haqida so\'rasangiz, men javob beraman.'

    if any(word in question_lower for word in ['kichik', 'small', 'otz', 'быстро']):
        return 'Hozir men lightweight режимда ishlayapman. Kattaroq modelni keyin o\'rnatishimiz mumkin.'

    if any(word in question_lower for word in ['rahmat', 'spasibo', 'thanks', 'thank']):
        return 'Arzamas! Yana savolingiz bo\'lsa, berasiz!'

    return (
        f'Sizning savolingiz: "{question[:100]}"\n\n'
        'Men aslida AI model orqali javob berayapman, lekin hozir xotira cheklanganida oddiy qoidalarga amal qilayapman. '
        'Ollama tayyor bo\'lsa, u yanada to\'liq javob beradi.'
    )


def get_ai_response(question: str) -> str:
    if GOOGLE_API_KEY:
        try:
            return ask_google_gemini(question)
        except Exception as exc:
            return f'Google Gemini API javob bera olmadi: {exc}.\n\n' + get_simple_response(question)

    if ollama_available():
        try:
            return ask_ollama(question)
        except Exception as exc:
            return f'Ollama javob bera olmadi: {exc}. Oddiy rejimga qaytmoqda.\n\n' + get_simple_response(question)

    return get_simple_response(question)


@app.get('/')
async def serve_html():
    html_path = Path(__file__).parent / 'chat.html'
    if html_path.exists():
        return FileResponse(html_path, media_type='text/html')
    return {'error': 'chat.html not found'}


@app.get('/api/status')
def status():
    if ollama_available():
        model = f'Ollama {OLLAMA_MODEL}'
    else:
        model = 'Simple AI (Rule-based)'
    return {
        'model': model,
        'device': 'cpu',
        'knowledge_size': 0,
        'status': 'Ready',
        'ollama_url': OLLAMA_URL,
    }


@app.post('/api/chat', response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = get_ai_response(request.question)
    history = request.history + [[request.question, answer]]
    return {'answer': answer, 'history': history}


if __name__ == '__main__':
    import uvicorn
    print('Starting lightweight AI chat server on http://127.0.0.1:8000')
    uvicorn.run(app, host='0.0.0.0', port=8000)
