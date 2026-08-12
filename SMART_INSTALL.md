# 🤖 Smart Install — Device-info se GitHub se APK

Aapke idea ke hisaab se: user apne device ki info bot me daalta hai →
GitHub (cloud) se uske device ke hisaab ka APK install hota hai.

---

## 🔒 Honest constraint
Android me **remote silent install** (bina user ke install dabaye) possible nahi.
Iska **real high-tech version** ye hai:

```
User → /device → Smart Install webapp (device info AUTO-detect)
   → bot ko DEVICE:{brand, model, android, abi, screen} bhejta hai
   → Backend GitHub Releases se us device ke hisaab ka APK URL nikalti hai
   → Bot user ko tailored direct APK download link bhejta hai
   → User tap → install ✅
```

GitHub = free APK host (Releases = permanent links + version track).
Device info se **split APK** (arm64/x86/model-specific) choose hota hai.

---

## 🗂️ Files
| File | Kaam |
|------|------|
| `telegram-webapp/device_info.html` | Device info auto-capture webapp (brand/model/android/abi/screen) |
| `backend/app.py` | `DEVICE:` handler + `build_apk_url()` (GitHub Releases se URL) |
| `backend/.env` | `GITHUB_REPO`, `APK_ASSET_PREFIX`, `APK_ASSET_SUFFIX` |

---

## 🚀 Setup

### 1. GitHub Releases pe APK upload karo
Split APK naming pattern:
```
app-<ABI>-android<major>-v<VER>.apk
```
Examples:
```
app-arm64-v8a-android14-v1.0.apk
app-armeabi-v7a-android7-v1.0.apk
app-x86_64-android12-v1.0.apk
```
1. GitHub → apne repo (`T1311`) → **Releases** → **Create a new release**
2. Tag: `v1.0.0` (koi bhi)
3. Saare split APKs as **assets** attach karo
4. **Publish release** → har APK ko permanent download link milta hai

### 2. BotFather me menu button (optional)
`/setmenubutton` → `device_info.html` ka URL → naam "📲 Smart Install"
Ab /device button se direct info capture hota hai.

---

## 🧪 Bot commands
- `/device` — info
- Webapp `DEVICE:` data → auto APK link reply

---

## 📌 Note
- Abhi `build_apk_url` GitHub API se `releases/latest` resolve karta hai (dynamic).
- Aapka repo abhi khali hai — pehle APK upload karna hoga.
- Device-specific split APK ke liye Android app me ABI-split build setup karna hoga (aage core banate waqt).
