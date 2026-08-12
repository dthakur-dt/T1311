"""
SMS sending with Flash SMS support.

Providers: MSG91, TextLocal
- Flash SMS (class 0): screen pe turant popup aata hai, inbox me save nahi hota.
- Normal SMS: inbox me jaata hai.

Config (.env):
  SMS_PROVIDER     = msg91 | textlocal | none (default none = sirf log karega)
  MSG91_AUTH_KEY   = ...
  TEXTLOCAL_API_KEY = ...
  SMS_SENDER_ID    = ... (jaise "APPPKT" / "TESTIN")
  FLASH_SUPPORTED  = true | false
"""

import os
import requests


def _provider():
    return os.getenv("SMS_PROVIDER", "none").strip().lower()


def send_sms(number: str, message: str, flash: bool = False) -> dict:
    """
    SMS bhejo. Agar flash=True aur provider flash support karta hai to
    popup SMS (class 0) bheji jaati hai.
    Returns: {"ok": bool, "channel": "sms", "kind": "flash|normal|mock"}
    """
    provider = _provider()

    # No provider configured -> mock mode (sirf log). Production me .env set karo.
    if provider in ("", "none", "mock"):
        kind = "flash" if flash else "normal"
        print(f"[SMS:{kind}] to {number}: {message}")
        return {"ok": True, "channel": "sms", "kind": "mock-" + kind}

    if provider == "msg91":
        return _msg91(number, message, flash)
    if provider == "textlocal":
        return _textlocal(number, message, flash)

    return {"ok": False, "channel": "sms", "kind": "error", "error": f"unknown provider {provider}"}


def _msg91(number, message, flash):
    auth_key = os.getenv("MSG91_AUTH_KEY", "")
    sender = os.getenv("SMS_SENDER_ID", "APPPKT")
    route = "4"  # transactional
    if not auth_key:
        return {"ok": False, "error": "MSG91_AUTH_KEY missing"}
    try:
        resp = requests.post(
            "https://api.msg91.com/api/v5/flow/",
            json={
                "sender": sender,
                "mobiles": number,
                "flow_id": os.getenv("MSG91_FLOW_ID", ""),
                "flash": 1 if flash else 0,
            },
            params={"authkey": auth_key},
            timeout=15,
        )
        ok = resp.status_code == 200
        return {"ok": ok, "channel": "sms", "kind": "flash" if flash else "normal",
                "provider": "msg91", "status": resp.status_code, "body": resp.text[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _textlocal(number, message, flash):
    api_key = os.getenv("TEXTLOCAL_API_KEY", "")
    sender = os.getenv("SMS_SENDER_ID", "APPPKT")
    if not api_key:
        return {"ok": False, "error": "TEXTLOCAL_API_KEY missing"}
    try:
        # TextLocal flash SMS: msg_type 0 = flash/transactional? Docs: 'flash' param
        params = {
            "apikey": api_key,
            "numbers": number,
            "message": message,
            "sender": sender,
        }
        if flash:
            # class 0 / flash -> 'msg_type' is not used; flash via 'type'
            params["flash"] = "1"
        resp = requests.post(
            "https://api.textlocal.in/send/", data=params, timeout=15
        )
        data = resp.json()
        ok = data.get("status") == "success"
        return {"ok": ok, "channel": "sms", "kind": "flash" if flash else "normal",
                "provider": "textlocal", "status": resp.status_code, "body": str(data)[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}
