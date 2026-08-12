# 🚀 Bot ko PERMANENTLY LIVE karo (Deploy Guide)

Aapka **source code GitHub pe safe hai** — ye guide sirf bot ko **cloud pe chalaane**
ke liye hai taaki wo 24x7 live rahe (bina mere sandbox ke).

---

## 🧠 Flow (kya hota hai)

```
Aapka GitHub repo (dthakur-dt/T1311)  ──┐
                                        ├─▶ Hosting platform (Koyeb/Render/Railway)
Deploy configs (Dockerfile, etc.)      ──┘     │  code ko 24x7 chalaata hai
                                               ▼
                                        Bot live (Telegram pe)
```

> Code GitHub pe hi rehta hai. Hosting bas usse copy karke chala deta hai.

---

## ✅ Sabse easy: Render (Blueprint) — 5 minute

### Step 1 — Saari deploy files commit karo
Maine ye files bana di hain (abhi commit + push karunga):
```
Dockerfile                  ← root pe (Render/Koyeb ise uthate hain)
backend/Dockerfile
backend/render.yaml         ← Render Blueprint config
railway.json                ← Railway config
```

### Step 2 — Render me connect karo
1. **render.com** → Signup (GitHub se login) — free
2. Dashboard → **New +** → **Blueprint**
3. Apna repo **`dthakur-dt/T1311`** select karo
4. Render `render.yaml` ko padh kar automatically service banayega

### Step 3 — Secrets set karo (dashboard me)
Service → **Environment** → ye add karo (secret):
```
BOT_TOKEN=<apna_bot_token>
GITHUB_TOKEN=<apna_github_token>
ADMIN_CHAT_ID=289240360
ROOT_NUMBER=<apna 10 digit root number>
```
> `render.yaml` me `sync: false` wale vars dashboard se bharne padte hain.

### Step 4 — Deploy
- Render auto-deploy karega (repo pe push pe bhi update hota hai)
- Deployed URL milega jaise `https://telegram-control-backend.onrender.com`
- Bot polling start ho jayega → **bot permanent live** 🎉

---

## 🎯 Option 2: Koyeb (free, bot hamesha ON)

1. **koyeb.com** → Signup (phone verify) — free
2. **Create Service** → **GitHub** → repo `dthakur-dt/T1311`
3. **Builder**: Dockerfile (root wala) — Koyeb use karega
4. **Environment variables** daalo (upar jaisi)
5. Deploy → bot live, free tier pe hamesha ON

---

## 🎯 Option 3: Railway

1. **railway.app** → Signup (GitHub) — trial me card chahiye
2. **New Project** → **Deploy from GitHub** → repo `dthakur-dt/T1311`
3. Railway `railway.json` + root Dockerfile use karega
4. **Variables** me BOT_TOKEN etc. daalo
5. Deploy → bot live

---

## 🔧 Secrets — kya kahaan (deploy me sabse important)

| Variable | Value | Zaroori? |
|----------|-------|----------|
| `BOT_TOKEN` | <apna_bot_token> | ✅ |
| `ADMIN_CHAT_ID` | 289240360 | ✅ |
| `GITHUB_TOKEN` | <apna_github_token> | ✅ build ke liye |
| `ROOT_NUMBER` | <apna 10 digit> | SMS ke liye |
| `GITHUB_REPO` | dthakur-dt/T1311 | optional |
| `SMS_PROVIDER` | none | SMS ke liye |

---

## 📌 Important notes
- **`BOT_TOKEN` aur `GITHUB_TOKEN`** ko deploy platform ke **secret env** me daalo — `.env` file repo me nahi hai (secret), isliye deploy pe manually set karna hoga.
- Jab bot deployed ho, Telegram me `/admin` bhejo → **Admin Console** milega.
- Hosting free tier me app **idle ho jaye** to (Render me 15 min) — Koyeb me aisa nahi hota (best for bot).
- Har baar repo push pe hosting **auto-redeploy** karti hai → hamesha latest code live.

---

## ✅ Aapke liye summary
1. Maine **deploy files ready** kar di hain.
2. Aapko bas ek **free hosting account** (Koyeb best / Render) + **GitHub connect** + **env vars** daalna hai.
3. Code **aapke GitHub pe hi rehta hai** — safe.
4. Bot **24x7 live** rahega.

> ⚠️ Security: Aapne BOT_TOKEN/GITHUB_TOKEN yahan share kiye hain. Production deploy ke baad
> inko **revoke** karke naye banana best hai (sirf deploy pe hi lage).
