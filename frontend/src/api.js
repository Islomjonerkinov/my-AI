export const API_ERROR_MSG =
  "Hatolik yuzaga keldi. Iltimos yana bir urinib ko'ring.";

export const MISSING_API_URL_MSG =
  "Vercelda VITE_API_URL o'rnatilmagan. Settings → Environment Variables → backend manzilingizni qo'shing.";

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

export function isApiConfigured() {
  return Boolean(API_BASE);
}

export function apiUrl(path) {
  return `${API_BASE}${path}`;
}

export function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const raw = String(reader.result || '');
      const base64 = raw.includes(',') ? raw.split(',')[1] : raw;
      resolve(base64);
    };
    reader.onerror = () => reject(new Error('read failed'));
    reader.readAsDataURL(file);
  });
}

export async function fetchStatus() {
  const res = await fetch(apiUrl('/api/status'));
  if (!res.ok) throw new Error(API_ERROR_MSG);
  return res.json();
}

export async function sendChat(payload) {
  const res = await fetch(apiUrl('/api/chat'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  let data = {};
  try {
    data = await res.json();
  } catch {
    /* ignore parse errors */
  }

  if (!res.ok) {
    throw new Error(API_ERROR_MSG);
  }

  return data;
}
