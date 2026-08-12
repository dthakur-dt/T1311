package com.example.telegrambotapp

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.appcompat.app.AppCompatDelegate

/**
 * Handles commands coming from the Telegram bot / WebApp
 * and applies them to the app's "features".
 *
 * Replace the placeholder actions below with your real app logic.
 */
class AppController(private val context: Context) {

    // Persistent state for each feature
    private val prefs = context.getSharedPreferences("app_controls", Context.MODE_PRIVATE)

    fun isOn(key: String): Boolean = prefs.getBoolean(key, false)
    private fun set(key: String, value: Boolean) = prefs.edit().putBoolean(key, value).apply()

    fun toggle(key: String): Boolean {
        val next = !isOn(key)
        set(key, next)
        return next
    }

    /**
     * Process a command string from the bot/WebApp and return
     * a human-readable reply to send back to the bot.
     */
    fun process(command: String): String {
        return when (command.uppercase()) {
            "TOGGLE_LIGHT" -> {
                val on = toggle("light"); setLight(on); "💡 Light ${if (on) "ON" else "OFF"} ho gayi"
            }
            "TOGGLE_FAN" -> {
                val on = toggle("fan"); "🌀 Fan ${if (on) "ON" else "OFF"} ho gaya"
            }
            "TOGGLE_DND" -> {
                val on = toggle("dnd"); "🔕 DND mode ${if (on) "ON" else "OFF"} ho gaya"
            }
            "TOGGLE_DARK" -> {
                val on = toggle("dark")
                applyDarkMode(on)
                "🌙 Dark mode ${if (on) "ON" else "OFF"} ho gaya"
            }
            "GET_STATUS" -> statusReport()
            "/start" -> "Hello! Main aapke app ko control karta hoon. WebApp button dabao ya commands bhejo (jaise /status)."
            "/status" -> statusReport()
            "/help" -> helpText()
            else -> {
                // Try to parse as "/command arg"
                val parts = command.trim().split(Regex("\\s+"))
                if (parts[0].equals("/light", true)) {
                    val on = if (parts.size > 1) parts[1].equals("on", true) else !isOn("light")
                    set("light", on); setLight(on)
                    "💡 Light ${if (on) "ON" else "OFF"}"
                } else if (parts[0].equals("/fan", true)) {
                    val on = if (parts.size > 1) parts[1].equals("on", true) else !isOn("fan")
                    set("fan", on)
                    "🌀 Fan ${if (on) "ON" else "OFF"}"
                } else {
                    "Unknown command: $command (try /help)"
                }
            }
        }
    }

    private fun statusReport(): String {
        return buildString {
            append("📊 App Status Report\n")
            append("———————————————\n")
            append("💡 Light:   ${if (isOn("light")) "ON" else "OFF"}\n")
            append("🌀 Fan:     ${if (isOn("fan")) "ON" else "OFF"}\n")
            append("🔕 DND:     ${if (isOn("dnd")) "ON" else "OFF"}\n")
            append("🌙 Dark:    ${if (isOn("dark")) "ON" else "OFF"}")
        }
    }

    private fun helpText(): String {
        return "Available:\n/light on|off\n/fan on|off\n/status\n\nYa WebApp control panel use karo!"
    }

    // ---- Example real actions you can wire up ----

    private fun setLight(on: Boolean) {
        // TODO: control actual hardware / broadcast an event
        context.sendBroadcast(Intent("com.example.LIGHT_CHANGED").putExtra("on", on))
    }

    private fun applyDarkMode(on: Boolean) {
        AppCompatDelegate.setDefaultNightMode(
            if (on) AppCompatDelegate.MODE_NIGHT_YES else AppCompatDelegate.MODE_NIGHT_NO
        )
    }

    fun getChatIntent(): Intent = Intent(Intent.ACTION_VIEW, Uri.parse("tg://resolve?domain=your_bot"))
}
