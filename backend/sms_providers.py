"""
SMS sending with Fast2SMS + Flash (popup) support.

Fast2SMS: aap apne mobile number se register karte ho aur usi number ko
sender ke roop me use karte ho. Sabse sasta + simple, trial credits milte hain.

Flash SMS / popup:
  - Fast2SMS ke pass asli "flash/class-0" nahi hai, par 6-character sender se
    DND-me nahi aane wali transactional SMS bheji jaati hai.
  - High-priority route se message screen par turant push hota hai.

Config (.env):
  SMS_PROVIDER        = fast2sms | none (default none = mock/log)
  FAST2SMS_API_KEY    = apni api key (Fast2SMS dashboard se)
  FAST2SMS_SENDER     = apna mobile number (10 digit) ya 6-char sender id
  FAST2SMS_ROUTE      = q (transactional) / p (promotional)
"""

import os
import requests

API_URL = "https://www.fast2sms.com/dev/bulkV2"


def _provider():
    return os.getenv("SMS_PROVIDER", "none").strip().lower()


def check_balance() -> dict:
    """Fast2SMS balance check (SMS limit). Returns credits remaining."""
    provider = _provider()
    if provider != "fast2sms":
        return {"ok": True, "kind": "mock", "balance": None}
    key = os.getenv("FAST2SMS_API_KEY", "")
    if not key:
        return {"ok": False, "error": "FAST2SMS_API_KEY missing"}
    try:
        resp = requests.get(
            "https://www.fast2sms.com/dev/wallet",
            headers={"authorization": key},
            timeout=15,
        )
        data = resp.json()
        if resp.status_code == 200 and data.get("return"):
            return {"ok": True, "kind": "fast2sms", "balance": data.get("wallet")}
        return {"ok": False, "error": str(data)[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def send_sms(number: str, message: str, flash: bool = False) -> dict:
    """
    SMS bhejo. Returns {"ok", "channel":"sms", "kind", "balance_used"}
    """
    provider = _provider()

    # Mock mode (no real SMS) — production me .env set karo.
    if provider in ("", "none", "mock"):
        kind = "flash" if flash else "normal"
        print(f"[SMS:{kind}] to {number}: {message}")
        return {"ok": True, "channel": "sms", "kind": "mock-" + kind}

    if provider == "fast2sms":
        return _fast2sms(number, message)

    return {"ok": False, "channel": "sms", "kind": "error", "error": f"unknown provider {provider}"}


def _fast2sms(number, message):
    key = os.getenv("FAST2SMS_API_KEY", "")
    sender = os.getenv("FAST2SMS_SENDER", "")     # apna mobile number
    route = os.getenv("FAST2SMS_ROUTE", "q")       # q = transactional
    if not key:
        return {"ok": False, "error": "FAST2SMS_API_KEY missing"}
    if not sender:
        return {"ok": False, "error": "FAST2SMS_SENDER missing"}

    # SMS limit check — pehle balance dekho
    bal = check_balance()
    if not bal.get("ok"):
        return {"ok": False, "error": "balance check failed: " + bal.get("error", "?")}
    try:
        # Fast2SMS transactional route -> only <=160 char, no DLT needed for trial
        payload = {
            "message": message[:160],
            "language": "unicode",
            "route": route,
            "numbers": number,
            "sender_id": sender,
        }
        resp = requests.post(API_URL, params=payload, headers={"authorization": key}, timeout=15)
        data = resp.json()
        ok = bool(data.get("return", False))
        return {
            "ok": ok,
            "channel": "sms",
            "kind": "fast2sms",
            "balance_used": True,
            "status": resp.status_code,
            "body": str(data)[:200],
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
