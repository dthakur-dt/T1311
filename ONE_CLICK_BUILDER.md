# 🔨 One-Click Builder — GitHub Actions se APK build

Ek button click karte hi app **GitHub Actions** par build hota hai aur APK
**GitHub Releases** par upload ho jata hai. Trigger 2 jagah se hota hai:
- **GitHub Actions** page par "Run workflow" button
- **Telegram** par `/build` command (backed through GitHub API dispatch)

---

## ⚡ Kaise kaam karta hai

```
[GitHub Actions "Run workflow" button]
                └────▶ Build APK workflow ──▶ split APKs ──▶ GitHub Releases
[Telegram /build v1.0.0]
                └────▶ Backend POST /api/build ──▶ GitHub API dispatch
```

- **GitHub Actions** build karta hai (JDK 17 + Android SDK + Gradle)
- Output: **split APKs by ABI** (`arm64-v8a`, `armeabi-v7a`, `x86_64`) + universal
- Softwares: `softprops/action-gh-release` APK ko **Release** pe upload karta hai
- Har APK ko **permanent download link** milta hai

---

## 🗂️ Files

| File | Kaam |
|------|------|
| `.github/workflows/build-apk.yml` | Build workflow (dispatch trigger) |
| `TelegramBotApp/gradlew` + wrapper | Gradle wrapper (CI build ke liye) |
| `TelegramBotApp/app/build.gradle` | ABI splits + versioned APK naming |
| `backend/app.py` | `/api/build` + `/build` telegram cmd + `trigger_github_build()` |
| `backend/.env` | `GITHUB_TOKEN` (repo scope) |

---

## 🚀 Use kaise karein

### Option A — GitHub Actions se (GitHub par hi)
1. GitHub → `T1311` → **Actions** tab
2. **Build APK** workflow → **Run workflow** button
3. `version` daalo (jaise `v1.0.0`) → **Run workflow**
4. Build khatam → **Releases** me APK milegi 🎉

### Option B — Telegram se (backend deployed ho to)
- Bot pe: `/build v1.0.0`
- Bot reply: "Build shuru! ... status dekhne ke liye github.com/.../actions"

### Option C — WebApp se
- `/api/build` POST → `{"version":"v1.0.0"}` (backend se)

---

## ⚙️ Setup (pehli baar)

1. **GITHUB_TOKEN** — backend `.env` me (repo scope wala token). Ye workflow dispatch + release upload permission deta hai. (Aapka wala token repo scope ka hai, kaam karega.)
2. **GitHub Actions enabled** hona chahiye repo pe (default on).
3. Build me **Gradle SDK/network** download hoti hai — pehli baar thoda time (2-5 min) lagega.

---

## 📌 Notes
- Build `workflow_dispatch` se trigger hota hai — bina browser ke API se bhi ho sakta hai.
- Release pe jitni baar bhi build karo, tag_existing=false to naya release banega.
- Split APKs ka naam `app-<abi>-v<version>.apk` (device matching Smart Install me use hota hai).
- **Production** me proper signing ke liye `signingConfig` me keystore secret add karo (abhi debug-signed demo hai).
- `.env` repo me nahi push hota (secret) — deploy pe manually set karna hai.
