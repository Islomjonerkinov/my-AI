# Vercelga muammosiz ulash (5 daqiqa)

Kelganingizda shu ro‘yxat bo‘yicha ketasiz. Hammasi GitHubda tayyor.

## 0. Oldin (bir marta)

- GitHub: https://github.com/Islomjonerkinov/my-AI
- [Vercel](https://vercel.com) va [Render](https://render.com) akkauntlari (GitHub bilan kirish mumkin)
- Google Gemini API kalit: https://aistudio.google.com/apikey

---

## 1. Backend (Render) — ~3 daqiqa

1. [dashboard.render.com](https://dashboard.render.com) → **New +** → **Blueprint**
2. Repongizni ulang: `Islomjonerkinov/my-AI`
3. `render.yaml` avtomatik ko‘rinadi → **Apply**
4. **Environment** → `GOOGLE_API_KEY` = kalitingizni yozing → Save
5. Deploy tugaguncha kuting (yashil **Live**)
6. Yuqoridagi manzilni nusxalang, masalan:  
   `https://my-ai-api.onrender.com`  
   (oxirida `/` yo‘q)

> Render bepul rejimda 50 daqiqadan keyin uxlaydi — birinchi so‘rov 30–60 soniya cho‘zilishi mumkin.

---

## 2. Frontend (Vercel) — ~2 daqiqa

1. [vercel.com/new](https://vercel.com/new) → GitHub → `my-AI` reponi tanlang
2. Sozlamalar (muhim):

   | Maydon | Qiymat |
   |--------|--------|
   | Root Directory | **bo‘sh qoldiring** |
   | Framework Preset | Vite (avtomatik) |
   | Build Command | *(bo‘sh — `vercel.json` boshqaradi)* |
   | Output Directory | *(bo‘sh — `vercel.json` boshqaradi)* |

3. **Environment Variables** → Add:
   - **Name:** `VITE_API_URL`
   - **Value:** Render manzili (1-qadamdan), masalan `https://my-ai-api.onrender.com`
4. **Deploy** bosing
5. Tugagach saytingiz: `https://my-ai-xxxx.vercel.app`

Agar chat ishlamasa: Vercel → Project → **Settings → Environment Variables** → `VITE_API_URL` to‘g‘rilang → **Deployments → Redeploy**

---

## 3. Tekshirish

1. Brauzerda Vercel manzilingizni oching
2. Tepadagi status: model nomi ko‘rinishi kerak (Server ulanmagan bo‘lmasin)
3. Matn yuboring — javob kelishi kerak
4. Rasm/ovoz uchun `GOOGLE_API_KEY` Renderda bo‘lishi shart

---

## Tez-tez muammolar

| Muammo | Yechim |
|--------|--------|
| Vercel build failed | Root Directory bo‘sh; `vercel.json` repoda borligini tekshiring |
| Server ulanmagan | `VITE_API_URL` qo‘yilganmi? Redeploy qiling |
| Hatolik yuzaga keldi | Render Live mi? API kalit to‘g‘rimi? Birinchi so‘rovda kuting |
| Render uxladi | Birinchi xabar yuborib 1 daqiqa kuting, qayta urinib ko‘ring |

---

## Lokal ish (ixtiyoriy)

```powershell
cd "c:\Users\Erkin\OneDrive\Desktop\IT\python\ai"
# .env fayl: GOOGLE_API_KEY=...
python simple_backend.py

cd frontend
npm install
npm run dev
```

Lokalda `VITE_API_URL` shart emas — Vite `/api` ni `localhost:8000` ga yo‘naltiradi.
