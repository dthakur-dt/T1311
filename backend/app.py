"""
Telegram Device-Control Backend
--------------------------------
Ek chhota backend jo:
  1. Telegram bot ko long-poll karta hai (getUpdates).
  2. Android apps ke heartbeat se devices ki "liveness" track karta hai.
  3. WebApp ko live/offline status deta hai.
  4. Install prompt ko Telegram bot ke through bhejta hai.

Token / config environment variables se aata hai (.env).
"""

import os
import threading
import time

from dotenv import load_dotenv
load_dotenv()  # .env se config load karo
from datetime import datetime, timezone

from sms_providers import send_sms, check_balance
import json

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")          # controller ka chat id
INSTALL_URL = os.getenv("INSTALL_URL", "https://example.com/app.apk")  # aapka APK link
HEARTBEAT_TTL = 45                                       # seconds — fresh ke liye
API = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None

# GitHub Releases se APK download (device-specific split APKs)
# Format: GITHUB_REPO = owner/repo ; APK asset naming pattern (ABI_ANDROID_VERSION)
GITHUB_REPO = os.getenv("GITHUB_REPO", "dthakur-dt/T1311")          # default aapka repo
APK_ASSET_PREFIX = os.getenv("APK_ASSET_PREFIX", "app")             # release asset prefix
APK_ASSET_SUFFIX = os.getenv("APK_ASSET_SUFFIX", ".apk")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")   # one-click build trigger ke liye (repo scope)

# ----------------------------------------------------------------------
# In-memory store (demo). Production me database use karein.
# ----------------------------------------------------------------------
last_seen = {}     # mobile_number -> epoch seconds (last heartbeat)
chat_ids = {}      # mobile_number -> telegram chat_id (jo app/register kiya)

app = FastAPI(title="Telegram Device Control Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def now_ts() -> float:
    return time.time()


def get_root_number() -> str:
    return os.getenv("ROOT_NUMBER", "").strip()

def root_registered() -> bool:
    """Root/admin registered hona chahiye tabhi device-SMS kaam karega."""
    return bool(get_root_number())


def require_root():
    if not root_registered():
        return {"ok": False, "error": "ROOT_NOT_REGISTERED",
                "message": "Root/admin ka mobile number register nahi hai. Pehle /api/root/setup se root number set karein."}
    return None


def is_live(number: str) -> bool:
    ts = last_seen.get(number)
    if ts is None:
        return False
    return (now_ts() - ts) <= HEARTBEAT_TTL


def tg_send(chat_id, text, buttons=None):
    if not API:
        return
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if buttons:
        payload["reply_markup"] = {
            "inline_keyboard": [[{"text": "📲 Install App", "url": INSTALL_URL}]]
        }
    try:
        requests.post(f"{API}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        print("send failed:", e)


# ----------------------------------------------------------------------
# API models
# ----------------------------------------------------------------------
class HeartbeatIn(BaseModel):
    number: str
    chat_id: int | None = None


class InstallIn(BaseModel):
    number: str
    channel: str = "auto"   # auto | flash | sms | telegram | both


# ----------------------------------------------------------------------
# REST endpoints (Android app + WebApp inke through baat karte hain)
# ----------------------------------------------------------------------
@app.post("/api/heartbeat")
def heartbeat(body: HeartbeatIn):
    """Android app har 20-30 sec pe call karta hai ye endpoint."""
    number = body.number.strip()
    if not number:
        return {"ok": False, "error": "number required"}
    last_seen[number] = now_ts()
    if body.chat_id:
        chat_ids[number] = body.chat_id
    return {"ok": True, "live": True}


@app.get("/api/status/{number}")
def status(number: str):
    """WebApp pe LIVE/OFFLINE dikhane ke liye."""
    number = number.strip()
    live = is_live(number)
    ts = last_seen.get(number)
    return {
        "number": number,
        "live": live,
        "last_seen": ts,
        "last_seen_human": (
            datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%H:%M:%S") if ts else None
        ),
    }


@app.post("/api/install")
def install(body: InstallIn):
    """
    Install prompt bhejo — admin 'installation choice' se channel chun sakta hai:
      - flash  : screen pe seedha popup (Flash SMS, class 0)
      - sms    : normal SMS
      - telegram : Telegram bot push
      - both   : Flash SMS + Telegram dono
      - auto   : pehle Telegram (agar number register hai), warna Flash SMS
    """
    number = body.number.strip()
    if not number:
        return {"ok": False, "error": "number required"}

    channel = (body.channel or "auto").strip().lower()
    if channel not in ("auto", "flash", "sms", "telegram", "both"):
        return {"ok": False, "error": f"invalid channel: {channel}"}

    msg_text = (
        f"📲 App install karein\n\nAapka device ({number}) abhi app se "
        f"connected nahi hai. App install karke login karein."
    )
    flash_msg = msg_text.replace("📲 ", "").replace("\n\n", " | ")

    results = []

    # --- Telegram ---
    def send_telegram():
        target_chat = chat_ids.get(number) or (int(ADMIN_CHAT_ID) if ADMIN_CHAT_ID else None)
        if not target_chat:
            return {"ok": False, "channel": "telegram", "error": "no chat_id known for number"}
        tg_send(target_chat, msg_text, buttons=True)
        return {"ok": True, "channel": "telegram", "sent_to": target_chat}

    # --- SMS (device/SIM-based ya gateway) ---
    def send_sms_choice(flash):
        # Authenticity: root registered hona jaroori hai
        blocked = require_root()
        if blocked:
            return {"ok": False, "channel": "sms", "error": "ROOT_NOT_REGISTERED",
                    "message": blocked["message"]}
        return send_sms(number, flash_msg, flash=flash)

    if channel in ("auto", "both", "telegram"):
        results.append(send_telegram())
    if channel in ("flash", "both"):
        results.append(send_sms_choice(flash=True))
    if channel in ("sms",):
        results.append(send_sms_choice(flash=False))

    if channel == "auto":
        # Telegram nai mila to flash SMS fallback
        if not results or not results[0].get("ok"):
            results.append(send_sms_choice(flash=True))

    # Agar koi SMS fail hua (limit/root nahi) to controller ko Telegram pe inform karo
    if ADMIN_CHAT_ID:
        for r in results:
            if r.get("channel") == "sms" and not r.get("ok"):
                tg_send(int(ADMIN_CHAT_ID),
                        f"⚠️ <b>SMS fail</b> {number}\nError: {r.get('message') or r.get('error', 'unknown')}",
                        buttons=False)

    return {"ok": True, "number": number, "channel": channel, "deliveries": results}


@app.get("/api/health")
def health():
    return {"ok": True, "live_devices": len([n for n in last_seen if is_live(n)])}


# ----------------------------------------------------------------------
# Root user setup (SMS provider / sender)
# ----------------------------------------------------------------------
class RootSetupIn(BaseModel):
    root_number: str | None = None       # root/admin ka mobile number
    sms_provider: str | None = None      # fast2sms | none
    api_key: str | None = None
    sender: str | None = None            # root ka number ya sender id


class BuildIn(BaseModel):
    version: str = "v1.0.0"
    tag_existing: bool = False


def trigger_github_build(version: str, tag_existing: bool) -> dict:
    """
    GitHub Actions workflow 'Build APK' ko dispatch karta hai (workflow_dispatch).
    Ye GitHub pe 'one-click build' button ka equivalent hai — bina browser ke.
    """
    if not GITHUB_TOKEN:
        return {"ok": False, "error": "GITHUB_TOKEN missing (repo scope ke saath set karo)"}
    try:
        r = requests.post(
            f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/build-apk.yml/dispatches",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
            },
            json={
                "ref": "main",
                "inputs": {
                    "version": version,
                    "tag_existing": "true" if tag_existing else "false",
                },
            },
            timeout=15,
        )
        if r.status_code == 204:
            return {"ok": True, "message": f"Build dispatch ho gaya: {version}"}
        return {"ok": False, "error": f"GitHub API status {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/build")
def build_app(body: BuildIn):
    """One-click build — GitHub Actions dispatch (Telegram / webapp se)."""
    if not GITHUB_TOKEN:
        return {"ok": False, "error": "GITHUB_TOKEN not configured in .env"}
    result = trigger_github_build(body.version, body.tag_existing)
    return result


@app.get("/api/root/setup")
def root_status():
    """Root setup ki current state (bina secret ke)."""
    return {
        "root_number": os.getenv("ROOT_NUMBER", ""),
        "sms_provider": os.getenv("SMS_PROVIDER", "none"),
        "sender": os.getenv("FAST2SMS_SENDER", ""),
        "configured": bool(os.getenv("FAST2SMS_API_KEY", "")),
    }


@app.post("/api/root/setup")
def root_setup(body: RootSetupIn):
    """
    Root user apna number + SMS provider config karta hai.
    Secrets ko .env me save karta hai (runtime me process env update hota hai).
    """
    if body.root_number:
        os.environ["ROOT_NUMBER"] = body.root_number.strip()
    if body.sms_provider:
        os.environ["SMS_PROVIDER"] = body.sms_provider.strip()
    if body.api_key:
        os.environ["FAST2SMS_API_KEY"] = body.api_key.strip()
    if body.sender:
        os.environ["FAST2SMS_SENDER"] = body.sender.strip()

    # Test balance check
    bal = check_balance()
    return {
        "ok": True,
        "root_number": os.getenv("ROOT_NUMBER", ""),
        "sms_provider": os.getenv("SMS_PROVIDER", "none"),
        "sender": os.getenv("FAST2SMS_SENDER", ""),
        "balance_check": bal,
    }


# ----------------------------------------------------------------------
# Telegram bot long-polling (background thread)
# ----------------------------------------------------------------------
def bot_poll():
    if not API:
        print("No BOT_TOKEN set. Bot polling disabled.")
        return
    offset = 0
    print("Bot polling started...")
    while True:
        try:
            r = requests.get(
                f"{API}/getUpdates",
                params={"offset": offset, "timeout": 20},
                timeout=30,
            )
            data = r.json()
            if not data.get("ok"):
                continue
            for upd in data.get("result", []):
                offset = upd["update_id"] + 1
                handle_update(upd)
        except Exception as e:
            print("poll error:", e)
            time.sleep(2)


def handle_update(upd):
    msg = upd.get("message") or upd.get("callback_query", {}).get("message")
    chat_id = (msg or {}).get("chat", {}).get("id")
    if not chat_id:
        return

    # WebApp se aayi data (sendData) — e.g. "CHECK:98XXX"
    web_data = (msg or {}).get("web_app_data", {}).get("data")
    if web_data:
        handle_command(chat_id, web_data, from_webapp=True)
        return

    text = (msg or {}).get("text", "") or ""
    if text:
        handle_command(chat_id, text, from_webapp=False)


def build_apk_url(abi: str, android: str) -> str:
    """
    Device info (ABI + Android version) se GitHub Release APK ka direct URL.
    Naming: <prefix>-<abi>-android<major>-v<ver>.apk
    Example: app-arm64-v8a-android11-v1.0.apk
    """
    try:
        major = int(android.split(".")[0])
    except Exception:
        major = 10
    # Android <8 (24) armeabi-v7a, baaki arm64 by default
    if major < 8:
        abi = "armeabi-v7a"
    asset = f"{APK_ASSET_PREFIX}-{abi}-android{major}-v{{VER}}.apk"
    # Latest release ke asset ko direct link me nahi daal sakte (version-dependent),
    # isliye GitHub releases/latest API se resolve karte hain.
    try:
        r = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest", timeout=10)
        data = r.json()
        ver = data.get("tag_name", "v1.0.0")
        for a in data.get("assets", []):
            name = a.get("name", "")
            if name.startswith(f"{APK_ASSET_PREFIX}-{abi}") and name.endswith(APK_ASSET_SUFFIX):
                return a.get("browser_download_url", name)
        # fallback: generic pattern
        fallback = f"{APK_ASSET_PREFIX}-{abi}-android{major}-{ver}{APK_ASSET_SUFFIX}"
        return f"https://github.com/{GITHUB_REPO}/releases/download/{ver}/{fallback}"
    except Exception as e:
        return f"https://github.com/{GITHUB_REPO}/releases/latest"


def handle_command(chat_id, text, from_webapp):
    text = text.strip()
    if not text:
        return

    # DEVICE:{...} — device info from Smart Install webapp
    if text.startswith("DEVICE:"):
        try:
            info = json.loads(text.split(":", 1)[1])
            brand = info.get("brand", "Android")
            model = info.get("model", "device")
            abi = info.get("abi", "arm64-v8a")
            android = info.get("android", "10")
            url = build_apk_url(abi, android)
            tg_send(
                chat_id,
                f"🤖 <b>Smart Install</b>\n\n"
                f"Device: {brand} {model}\n"
                f"Android: {android}\n"
                f"ABI: {abi}\n\n"
                f"Ye APK aapke device ke liye optimized hai. Download karke install karein:\n\n"
                f"<a href='{url}'>📲 Download APK</a>\n\n"
                f"(Source: GitHub Releases)",
            )
        except Exception as e:
            tg_send(chat_id, f"⚠️ Device info parse error: {e}\nUsage: /device")
        return

    # /build — one-click build (GitHub Actions dispatch)
    if text.lower().startswith("/build"):
        parts = text.split()
        version = parts[1] if len(parts) >= 2 else "v1.0.0"
        res = trigger_github_build(version, tag_existing=False)
        if res.get("ok"):
            tg_send(chat_id, f"🔨 <b>Build shuru!</b>\nVersion: {version}\n\n"
                             f"GitHub Actions pe build chal raha hai.\n"
                             f"Jab complete ho, APK GitHub Releases pe aa jayega.\n\n"
                             f"Status dekhne ke liye: https://github.com/{GITHUB_REPO}/actions")
        else:
            tg_send(chat_id, f"⚠️ Build trigger nahi hua.\nError: {res.get('error')}")
        return

    # /device — smart install webapp link bhejo
    if text.lower().startswith("/device"):
        tg_send(
            chat_id,
            f"🔧 <b>Device Info</b>\n\n"
            f"Device info auto-capture ke liye niche button kholo, phir 'APK link lein' dabao.\n\n"
            f"/device_webapp_open  (ya menu button se)",
        )
        return

    # /register 98XXXXXXXX
    if text.lower().startswith("/register"):
        parts = text.split()
        if len(parts) >= 2:
            number = parts[1].strip()
            chat_ids[number] = chat_id
            tg_send(chat_id, f"✅ Number <b>{number}</b> register ho gaya. Ab app heartbeat bhejne lagao.")
        return

    # /status 98XXXXXXXX  (chat me reply)
    if text.lower().startswith("/status"):
        parts = text.split()
        if len(parts) >= 2:
            number = parts[1].strip()
            live = is_live(number)
            if live:
                tg_send(chat_id, f"🟢 <b>{number}</b> — LIVE")
            else:
                tg_send(
                    chat_id,
                    f"🔴 <b>{number}</b> — OFFLINE\n\nIsse app install karne ka prompt bhejna hai?",
                    buttons=True,
                )
        else:
            tg_send(chat_id, "Usage: /status 98XXXXXXXX")
        return

    # CHECK:98XXX  (webapp se aaya)
    if text.startswith("CHECK:"):
        number = text.split(":", 1)[1].strip()
        if is_live(number):
            tg_send(chat_id, f"🟢 {number} — LIVE")
        else:
            tg_send(chat_id, f"🔴 {number} — OFFLINE", buttons=True)
        return

    # Install command from chat
    if text.lower().startswith("/install"):
        parts = text.split()
        if len(parts) >= 2:
            number = parts[1].strip()
            tg_send(chat_id, f"📲 <b>{number}</b> ke liye install prompt:", buttons=True)
        return

    # /help
    if text.lower() in ("/help", "/start"):
        tg_send(
            chat_id,
            "Available commands:\n"
            "/register 98XXXXXXXX — apna number register karo\n"
            "/status 98XXXXXXXX — live/offline check\n"
            "/install 98XXXXXXXX — install prompt bhejo\n"
            "/device — smart install (device info → APK)\n"
            "/build — one-click build (GitHub Actions)",
        )


# ----------------------------------------------------------------------
# Start bot polling on startup
# ----------------------------------------------------------------------
@app.on_event("startup")
def on_start():
    t = threading.Thread(target=bot_poll, daemon=True)
    t.start()
