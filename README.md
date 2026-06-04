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

Agar `GOOGLE_API_KEY` o‘rnatilgan bo‘lsa, backend `gemini-flash-latest` modeliga so‘rov yuboradi va frontendga natijani qaytaradi. **Rasm va ovoz** yuborish uchun ham `GOOGLE_API_KEY` kerak.

### Frontend imkoniyatlari

- Yangi yengil dizayn (chat markazida)
- Rasm yuklash (📷) va ovoz (🎤 yozish yoki 📎 fayl)
- API ishlamasa: `Hatolik yuzaga keldi. Iltimos yana bir urinib ko'ring.`

### Vercel + GitHub

| Qism | Vercel? | Izoh |
|------|---------|------|
| **React frontend** (`frontend/`) | Ha | GitHub repo ulab, Root Directory = `frontend` |
| **Python backend** (`simple_backend.py`) | Yo‘q* | Og‘ir model / uzoq so‘rovlar uchun [Render](https://render.com), [Railway](https://railway.app) yoki [Fly.io](https://fly.io) yaxshiroq |

\* Faqat Gemini API chaqiradigan yengil backendni Vercel Serverless Python bilan ham qilish mumkin, lekin `main.py` dagi katta PyTorch modeli Vercelga mos emas.

**Deploy qadamlari:**

1. Repo GitHubga push qiling (`vercel.json` loyiha ildizida bo‘lishi kerak).
2. [vercel.com](https://vercel.com) → New Project → repongizni tanlang.
3. **Root Directory** — ikkala variant ishlaydi:
   - **Bo‘sh qoldiring** (ildiz) — `vercel.json` avtomatik `frontend/` dan build qiladi
   - Yoki `frontend` deb yozing — faqat frontend papkasi
4. **Environment Variables** (majburiy): `VITE_API_URL` = `https://your-api.onrender.com` (oxirida `/` bo‘lmasin)
5. Backendni alohida hostingda ishga tushiring va `GOOGLE_API_KEY` ni u yerda qo‘ying.

### Vercelda tez-tez chiqadigan xatolar

| Xato / belgi | Sabab | Yechim |
|--------------|--------|--------|
| `package.json` topilmadi | Root Directory noto‘g‘ri | Root = bo‘sh yoki `frontend`; yangi `vercel.json` ni push qiling |
| Build failed / `npm` | `node_modules` yuklangan | GitHubga faqat kod; `node_modules` commit qilmang |
| Sayt ochiladi, lekin chat ishlamaydi | Backend Vercelda yo‘q | `VITE_API_URL` ni Vercel → Settings → Environment Variables ga qo‘ying, **Redeploy** |
| `Hatolik yuzaga keldi…` | API ishlamayapti | Backend ishlayaptimi? URL to‘g‘rimi? `GOOGLE_API_KEY` bormi? |
| 404 `/api/...` | Frontend API ni o‘zida qidiradi | `VITE_API_URL` bo‘lmasa so‘rovlar Vercelga ketadi — env qo‘shing |

Lokal ishga tushirish (yengil backend):

```bash
python simple_backend.py
cd frontend && npm run dev
```

# my-AI
# AI-2
