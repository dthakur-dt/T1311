# 🌐 Telegram WebApp Control Panel — Setup Guide

Aapka bot ab Android app ke features **Telegram ke andar khulne wale WebApp** se control karega.
Ye control panel bot me ek button dabate hi khulta hai.

---

## 🎯 Flow kaisa hai

```
User → BotFather ke set button → WebApp khula (control panel)
   → User button dabata hai (Light ON etc.)
   → WebApp.sendData("TOGGLE_LIGHT") bot ko jaata hai
   → Bot (getUpdates) ye command app ko deta hai
   → Android app us feature ko ON/OFF karta hai
   → App reply bhejta hai: "💡 Light ON ho gayi"
```

---

## 📌 Setup ke 3 steps

### Step 1 — WebApp ko host karo (HTTPS link chahiye)
WebApp ki file: **`index.html`** (is folder me)

3 options:
- **Sabse easy:** is project ko **GitHub Pages** / **Netlify** / **Vercel** pe deploy karo → milta hai HTTPS link
- **Ya**: aapke paas koi hosting/server hai to `index.html` wahin dalo
- **Testing ke liye:** mujhe live preview ka URL de do (jo browser me khula hai) — bas wo URL BotFather me lagana hai

> ⚠️ Telegram WebApp ko **HTTPS** URL chahiye hota hai, iske bina kaam nahi karega.

### Step 2 — BotFather me WebApp button set karo
1. Telegram me **BotFather** kholo
2. `/mybots` → apna bot select karo
3. **Bot Settings** → **Menu Button** (ya `/setmenubutton`)
4. WebApp URL paste karo (jo Step 1 me mila)
5. **Done** ✅

Ab bot kholne pe menu button se control panel khulega.

### Step 3 — Commands set karo (optional)
BotFather → `/mybots` → bot → **Edit Bot** → **Edit Commands**:

```
light - Light on/off
fan - Fan on/off
status - Sab features ki state
help - Help
```

---

## 🎛️ WebApp ke controls

| Button | Command | App me kya hota hai |
|--------|---------|---------------------|
| 💡 Light | `TOGGLE_LIGHT` | Light feature toggle |
| 🌀 Fan | `TOGGLE_FAN` | Fan feature toggle |
| 🔕 DND | `TOGGLE_DND` | Notifications band/on |
| 🌙 Dark | `TOGGLE_DARK` | Dark mode |
| 📊 Status | `GET_STATUS` | Pura status report |

---

## 🔧 Apne hisaab se badalna

- **Naye features** jodne ke liye → `index.html` me ek naya `.card` add karo + `AppController.kt` me us command ka case likho.
- **Asli hardware/action** jodne ke liye → `AppController.kt` me `setLight()`/`setFan()` ke andar apna real code (jaise Arduino/ESP32 ko request bhejna) daalo.

---

## 💬 Bot pe direct commands bhi chalte hain
WebApp ke bina bhi bot pe type karke chala sakte ho:
- `/light on` , `/light off`
- `/fan on` , `/fan off`
- `/status`
- `/help`
