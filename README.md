# AI Assistant with React Frontend and FastAPI Backend

## Tuzilishi

- `main.py` - mavjud model va chat funksiyalari
- `backend.py` - FastAPI API serveri
- `frontend/` - React + Vite web UI
- `requirements.txt` - Python paketlari

## O'rnatish

1. Python paketlarini o'rnating:
```bash
python -m pip install -r requirements.txt
```

2. React frontend uchun paketlarni o'rnating:
```bash
cd frontend
npm install
```

## Ishga tushirish

### Backend

```
python backend.py
```

Agar `uvicorn` bilan ishga tushirishni istasangiz:

```bash
python -m uvicorn backend:app --reload
```

### Frontend

```bash
cd frontend
npm run dev
```

## Foydalanish

- Backend FastAPI `http://127.0.0.1:8000`
- React UI `http://127.0.0.1:5173`

## Modelni kuchaytirish

Agar sizda kuchli model bo'lsa, muhit o'zgaruvchisidan foydalaning:

```bash
set AI_MODEL=tiiuae/falcon-7b-instruct
python backend.py
```

Yoki PowerShellda:

```powershell
$env:AI_MODEL = 'tiiuae/falcon-7b-instruct'
python backend.py
```

## API kalitni xavfsiz saqlash

Agar siz masofaviy model yoki Google Gemini kabi xizmat ishlatayotgan bo'lsangiz, kalitni kodga to‘g‘ridan-to‘g‘ri yozmang. `AI` papka ichida `.env` fayl yarating va quyidagicha yozing:

```env
GOOGLE_API_KEY=your_api_key_here
```

Yoki ba'zi bir serverlar uchun `OPENAI_API_KEY` tanlang.

So‘ng `.gitignore` fayliga `.env` qo‘shilgan, shuning uchun u versiyalashga yuklanmaydi.

> Eslatma: real kalitni hech qachon Internetga yoki umumiy papkaga joylamang.

### Google Gemini API ni ishlatish

Agar `GOOGLE_API_KEY` o‘rnatilgan bo‘lsa, backend `gemini-flash-latest` modeliga so‘rov yuboradi va frontendga natijani qaytaradi.
# my-AI
