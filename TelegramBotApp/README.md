# 🤖 Telegram Bot Android App

Ek simple **Android app** (Kotlin) jo aapke **Telegram bot** se chat karta hai.
App bot ko messages bhejta hai aur bot ke replies live dikhata hai (long-polling).

---

## 🛠️ Ye project kaise chalayein (Android Studio)

### 1. Requirements
- **Android Studio** (latest, me Jellyfish/Hedgehog)
- Android SDK **34**
- Java **17** (Android Studio me built-in)

### 2. Steps
1. **Download** is pura folder (TelegramBotApp) apne computer par.
2. Android Studio kholein → **File → Open** → `TelegramBotApp` folder select karein.
3. Android Studio jaldi hi apne aap Gradle sync karega (pehli baar thoda time lagega).
4. **Phone/Emulator** me app chalao (USB debugging on karke, ya emulator se).

### 3. Bot Token daalein
1. Telegram me **BotFather** kholein → `/newbot` chalaayein → bot banayein.
2. Milne wala **token** copy karein (jaise `1234567890:AA...`).
3. App me top-right **edit (✎)** icon dabayein → token paste karein → **Save**.
4. **Sabse pehle** apne bot ko Telegram pe ek message bhejein (taaki app ko chat ID mil jaye).
5. Ab app me bheje gaye messages aur bot ke replies dikhenge.

---

## 📁 Project Structure

```
TelegramBotApp/
├── build.gradle
├── settings.gradle
├── gradle.properties
└── app/
    ├── build.gradle
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/com/example/telegrambotapp/
        │   ├── MainActivity.kt      ← main UI + logic
        │   ├── TelegramApi.kt       ← Retrofit API interface
        │   ├── Models.kt            ← data classes
        │   └── MessageAdapter.kt    ← chat list adapter
        └── res/
            ├── layout/
            │   ├── activity_main.xml
            │   ├── item_message.xml
            │   └── dialog_settings.xml
            ├── values/
            │   ├── colors.xml
            │   ├── strings.xml
            │   └── themes.xml
            └── drawable/
```

---

## ⚙️ Kaise kaam karta hai

| Cheez | Detail |
|------|--------|
| **Send message** | `POST /bot<token>/sendMessage` with `chat_id` + `text` |
| **Receive replies** | `GET /bot<token>/getUpdates` long-polling (offset+timeout) |
| **Network** | Retrofit + OkHttp + Gson |
| **Async** | Kotlin Coroutines |

---

## 🎨 Apne hisaab se badalna (customize)

- **App ka naam** → `app/src/main/res/values/strings.xml`
- **Rang** → `colors.xml` (Telegram blue `#229ED9`)
- **Chat style** → `item_message.xml` + `drawable/bg_message_*.xml`
- **Bot ka behavior** → aapka bot server-side control karta hai (BotFather se setup)

---

## ⚠️ Important Notes

- **Chat ID**: App ko kaam karne se pehle bot ko koi ek message Telegram pe chahiye.
- **Internet permission** already added hai manifest me.
- Production ke liye `buildApi` me token hard-code karna ho ya secure storage use karein.
- Ye project **sirf demo/dikhane ke liye** basic hai — real app me security aur error handling improve karein.

---

## 🚀 Aage kya?

Batao agar chahiye toh:
- 🔐 Secure login (Telegram `loginWidget` / Auth)
- 📦 Bot se images/files bhejna aur dikhana
- 🎛️ Bot se device control (IoT) wala feature
- 🌐 Multi-language / dark theme
