# 📡 Live Check + Install Prompt — Feature Guide

Ye feature abhi add kiya gaya hai. Pura flow, architecture, aur setup yahan hai.

---

## 🎯 Ye kya karta hai

1. **WebApp** me aap mobile number daalte hain.
2. WebApp backend se us number ki **liveness** puchta hai.
3. Agar device ka app **heartbeat** bhej raha hai → **🟢 LIVE** dikhta hai.
4. Agar nahi → **🔴 OFFLINE** + ek **install popup** khulta hai.
5. Popup se **Telegram bot** ke through us user ko install prompt bheja ja sakta hai.
6. Ye same kaam **bot chat** me bhi hota hai: `/status 98XXXXXXXX`.

---

## 🧠 Architecture

```
┌─────────────┐   heartbeat (POST /api/heartbeat)   ┌──────────────────┐
│ Android App │ ───────────────────────────────────▶ │     Backend      │
└─────────────┘                                      │  (FastAPI)       │
                                                     │  • liveness store │
┌─────────────┐   GET /api/status/{num}             │  • bot long-poll  │
│  WebApp     │ ───────────────────────────────────▶ │                  │
└─────────────┘                                      └──────────────────┘
                                                            │  install prompt
                                                            ▼
                                                     ┌─────────────┐
                                                     │ Telegram Bot│
                                                     └─────────────┘
```

**Key idea:** Phone ko directly ping nahi kar sakte (no public IP). Isliye app apni liveness **backend ko heartbeat** se batata hai, aur backend ise store karke webapp/bot ko batata hai.

---

## 🗂️ Files

| File | Kya hai |
|------|---------|
| `backend/app.py` | FastAPI backend — heartbeat, status, install, bot polling |
| `backend/.env` | Config (BOT_TOKEN, ADMIN_CHAT_ID, INSTALL_URL) |
| `telegram-webapp/index.html` | WebApp — live check + install popup |
| `TelegramBotApp/.../Config.kt` | Backend URL config |
| `TelegramBotApp/.../HeartbeatManager.kt` | App heartbeat sender |
| `TelegramBotApp/.../ui/settings/SettingsFragment.kt` | Mobile number + token save |

---

## 🚀 Setup (production ke liye)

### 1. Backend deploy karo
- `backend/` folder ko kisi server pe chalao (Railway / Render / Vercel / koi VPS).
- `.env` me apna `BOT_TOKEN`, `ADMIN_CHAT_ID`, `INSTALL_URL` (APK link) daalo.
- Backend ka **public URL** note karo, jaise `https://mybackend.up.railway.app`.

### 2. WebApp me URL lagao
- `telegram-webapp/index.html` me:
  ```js
  const BACKEND = "https://mybackend.up.railway.app";
  ```
- WebApp ko HTTPS pe host karo (GitHub Pages / Netlify / Vercel).
- BotFather → `/setmenubutton` → WebApp URL set karo.

### 3. App me URL lagao
- `Config.kt` me:
  ```kotlin
  const val BACKEND_URL = "https://mybackend.up.railway.app"
  ```
- App ka APK banakar install prompt me wahi URL daalo (`INSTALL_URL`).

### 4. App use karo
- App → **Settings** → bot token + **mobile number** daalo → Save.
- Ab app backend ko live report karta hai.
- WebApp / bot me number check karo → LIVE / OFFLINE.

---

## 🤖 Bot chat commands

| Command | Kaam |
|---------|------|
| `/register 98XXXXXXXX` | Number ko apne chat se jodo |
| `/status 98XXXXXXXX` | Live/offline check |
| `/install 98XXXXXXXX` | Install prompt bhejo |
| `/help` | Commands list |

---

## ⚠️ Demo/sandbox notes
- Abhi ye sandbox me hai — `BACKEND_URL` abhi `localhost` placeholder pe hai.
- Real end-to-end ke liye backend public hone par `Config.kt` aur webapp ka URL badalna hoga.
- `last_seen` in-memory hai — backend restart pe reset hota hai. Production me database/Redis use karein.
- Telegram long-polling sirf **ek** consumer kar sakta hai (backeend karta hai). Android app ab khud getUpdates **nahi** poll karta — wo heartbeat se report karta hai.
