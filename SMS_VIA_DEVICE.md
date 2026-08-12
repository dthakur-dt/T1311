# 📱 SMS via Device (Aapki SIM ke SMS limit se)

## Aapka idea
Webapp me jo bhi number daala jaye, message **aapke device ke SIM** (Airtel/Jio/Vi)
se bheja jaye. Sending limit = aapke SIM ke recharge me milne wale SMS credits.

## 🔑 Technical reality (samajhna zaroori)
- **WebApp/browser SMS nahi bhej sakta.** Browser ya Telegram webapp ko SIM access nahi hota.
- SMS bhejne ke 2 raste:
  1. **SMS Gateway** (Fast2SMS/MSG91) — paid, provider server se, SIM use nahi karta
  2. **Android app + SIM** — app `SMSManager` se bhejta hai, aapki SIM ke SMS credits khatam karta hai

Aapne rasta **#2** chuna hai → **device-based SMS**.

## 🏗️ Architecture (device-based)

```
WebApp (admin number daalta hai)
   │  POST /api/install { number }
   ▼
Backend (root verified hona chahiye)
   │  realtime channel → root ke phone pe installed Control App ko batata hai
   ▼
Control App (root ke phone, SMS permission wala)
   │  apni SIM ke SMSManager se SMS bhejta hai
   │  SMS count local track (limit)
   ▼
Target user ko SMS "App install karein ..."
```

## ✅ Root Registration (aapne bola — must hai)
- Root/admin ka **mobile number register** hone par hi SMS kaam karta hai.
- Bina registered root ke: `/api/install` aur device-SMS **blocked** → error "root not registered".
- Root verify: backend `.env` me `ROOT_NUMBER` set + control app usi SIM se connected.

## 📊 SMS limit handling
- Control app har SMS bhejne se pehle local `sms_count` check karta hai.
- Limit configurable (SIM recharge ke hisaab se), jaise `DAILY_SMS_LIMIT`.
- Limit cross hone pe: SMS nahi bhejta + Telegram pe controller ko notify.
- Count ko reset daily / jab recharge ho.

## 📁 Files
| File | Kaam |
|------|------|
| `backend/app.py` | Root-registration check, install endpoint |
| `TelegramBotApp/.../SmsSender.kt` | (next step) App ke SMSManager se SIM SMS bhejna |
| `TelegramBotApp/.../SmsCounter.kt` | (next step) Daily SMS limit track |

> ⚠️ **Note:** Ye design abhi backend + doc hai. `SmsSender.kt` aur `SmsCounter.kt` ko next step me
> root ke phone pe deploy karna hai — uske liye Control App ka module banega.
