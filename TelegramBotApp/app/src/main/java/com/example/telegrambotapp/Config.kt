package com.example.telegrambotapp

/**
 * Central config. Production me apna backend URL yahan daalein.
 */
object Config {
    // Aapke backend ka public URL (jahan backend/app.py deployed hai)
    // Sandbox/testing ke liye localhost use karein.
    const val BACKEND_URL = "https://YOUR_BACKEND_URL_HERE"

    // Heartbeat interval (seconds) — app kitni baar backend pe live-report karega
    const val HEARTBEAT_INTERVAL_SEC = 20L
}
