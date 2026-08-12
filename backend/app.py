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
    """Install prompt ko bot ke through target user ko bhejta hai."""
    number = body.number.strip()
    if not number:
        return {"ok": False, "error": "number required"}
    target_chat = chat_ids.get(number) or (int(ADMIN_CHAT_ID) if ADMIN_CHAT_ID else None)
    if not target_chat:
        return {"ok": False, "error": "no chat_id known for this number"}
    tg_send(
        target_chat,
        f"📲 <b>App install karein</b>\n\nAapka device ({number}) abhi app ke saath connected nahi hai. "
        f"App install karke login karein, phir yahan live dikhega.",
        buttons=True,
    )
    return {"ok": True, "sent_to": target_chat}


@app.get("/api/health")
def health():
    return {"ok": True, "live_devices": len([n for n in last_seen if is_live(n)])}


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


def handle_command(chat_id, text, from_webapp):
    text = text.strip()
    if not text:
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
            "/install 98XXXXXXXX — install prompt bhejo",
        )


# ----------------------------------------------------------------------
# Start bot polling on startup
# ----------------------------------------------------------------------
@app.on_event("startup")
def on_start():
    t = threading.Thread(target=bot_poll, daemon=True)
    t.start()
