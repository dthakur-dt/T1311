package com.example.telegrambotapp

import android.content.Context
import android.content.SharedPreferences
import kotlinx.coroutines.*
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/**
 * Heartbeat manager — app ki liveness ko backend ko report karta hai.
 * Settings me jo mobile number save hai, usi ke saath backend pe jata hai.
 */
class HeartbeatManager(private val context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("telegram_bot", Context.MODE_PRIVATE)

    private var job: Job? = null

    /** Heartbeat loop shuru karo (agar number set hai to). */
    fun start() {
        job?.cancel()
        job = CoroutineScope(Dispatchers.IO).launch {
            while (isActive) {
                report()
                delay(Config.HEARTBEAT_INTERVAL_SEC * 1000)
            }
        }
    }

    fun stop() {
        job?.cancel()
        job = null
    }

    private fun report() {
        val number = prefs.getString("mobile_number", "").orEmpty()
        if (number.isEmpty()) return  // number set nahi hai, kuch nahi karte

        val chatId = prefs.getLong("chat_id", 0L)
        val base = Config.BACKEND_URL.trimEnd('/')

        try {
            val url = URL("$base/api/heartbeat")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.doOutput = true
            conn.setRequestProperty("Content-Type", "application/json")
            conn.connectTimeout = 5000
            conn.readTimeout = 5000

            val json = JSONObject().apply {
                put("number", number)
                if (chatId != 0L) put("chat_id", chatId)
            }
            conn.outputStream.use { it.write(json.toString().toByteArray()) }
            conn.inputStream.close()
            conn.disconnect()
        } catch (e: Exception) {
            // ignore — network/offline, agle cycle me try karega
        }
    }
}
