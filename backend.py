from typing import List
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title='AI Assistant API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

try:
    from main import MODEL_NAME, chat_with_model, get_device, load_knowledge, load_model
    print('Loading model for API...')
    tokenizer, model = load_model(MODEL_NAME)
    knowledge = load_knowledge()
    MODEL_LOADED = True
except Exception as e:
    print(f'Model yuklanmadi: {e}')
    MODEL_LOADED = False
    tokenizer = None
    model = None
    knowledge = []
    MODEL_NAME = 'unknown'

@app.get('/')
async def serve_html():
    html_path = Path(__file__).parent / 'chat.html'
    if html_path.exists():
        return FileResponse(html_path, media_type='text/html')
    return {'message': 'AI Assistant API ishlayapti!'}

class ChatRequest(BaseModel):
    question: str
    history: List[List[str]] = []

class ChatResponse(BaseModel):
    answer: str
    history: List[List[str]]

class KnowledgeRequest(BaseModel):
    note: str

@app.get('/api/status')
def status():
    return {
        'model': MODEL_NAME,
        'device': get_device() if MODEL_LOADED else 'cpu',
        'knowledge_size': len(knowledge),
        'model_loaded': MODEL_LOADED,
    }

@app.post('/api/chat', response_model=ChatResponse)
def chat(request: ChatRequest):
    if not MODEL_LOADED:
        return {'answer': 'Model yuklanmagan. Server qayta ishga tushiring.', 'history': request.history}
    answer = chat_with_model(tokenizer, model, request.question, request.history)
    history = request.history + [[request.question, answer]]
    return {'answer': answer, 'history': history}

@app.post('/api/knowledge')
def add_knowledge(request: KnowledgeRequest):
    note_text = request.note.strip()
    if not note_text:
        return {'message': 'Iltimos, biror matn kiriting.'}
    knowledge.append(note_text)
    return {'message': "Bilim bazasiga qo'shildi.", 'size': len(knowledge)}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend:app', host='0.0.0.0', port=8000, reload=True)