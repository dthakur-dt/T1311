package com.example.telegrambotapp

import android.annotation.SuppressLint
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.inputmethod.InputMethodManager
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.telegrambotapp.databinding.ActivityMainBinding
import kotlinx.coroutines.*
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var adapter: MessageAdapter
    private val messages = mutableListOf<ChatMessage>()

    private var chatId: Long = 0
    private var updateOffset: Long = 0
    private var pollingJob: Job? = null
    private lateinit var controller: AppController

    // Settings keys
    private val prefs by lazy {
        getSharedPreferences("telegram_bot", Context.MODE_PRIVATE)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        controller = AppController(this)
        setupRecyclerView()
        setupInput()

        // Try to start with saved token
        val savedToken = prefs.getString("bot_token", null)
        if (!savedToken.isNullOrEmpty()) {
            startPolling(savedToken)
        } else {
            binding.statusText.text = getString(R.string.set_token)
            openSettings(null)
        }
    }

    private fun setupRecyclerView() {
        adapter = MessageAdapter(messages)
        binding.messagesRecycler.layoutManager = LinearLayoutManager(this)
        binding.messagesRecycler.adapter = adapter
    }

    private fun setupInput() {
        binding.sendButton.setOnClickListener { onSendClick() }
        binding.messageInput.setOnEditorActionListener { _, _, _ ->
            onSendClick()
            true
        }
    }

    // ---- Send a message to the bot ----
    fun onSendClick(view: View? = null) {
        val text = binding.messageInput.text?.toString()?.trim().orEmpty()
        if (text.isEmpty()) return

        val token = prefs.getString("bot_token", null).orEmpty()
        if (token.isEmpty()) {
            Toast.makeText(this, getString(R.string.set_token), Toast.LENGTH_SHORT).show()
            openSettings(null)
            return
        }
        if (chatId == 0L) {
            Toast.makeText(this, "Pehle Telegram pe bot ko ek message bhejein (chat ID save ho jayegi).", Toast.LENGTH_LONG).show()
            return
        }

        // Clear input and hide keyboard
        binding.messageInput.setText("")
        hideKeyboard()

        // Add user message to UI immediately
        adapter.addMessage(ChatMessage(true, text, currentTime()))
        binding.messagesRecycler.scrollToPosition(messages.size - 1)

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val api = buildApi(token)
                val res = api.sendMessage(SendMessageRequest(chatId, text))
                if (!res.isSuccessful) {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, getString(R.string.send_failed), Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    // ---- Long polling for bot replies ----
    private fun startPolling(token: String) {
        binding.statusText.text = getString(R.string.connected)
        pollingJob?.cancel()
        pollingJob = CoroutineScope(Dispatchers.IO).launch {
            try {
                val api = buildApi(token)
                // Get updates continuously
                while (isActive) {
                    val res = api.getUpdates(offset = updateOffset, timeout = 15)
                    if (res.isSuccessful) {
                        val updates = res.body()?.result ?: emptyList()
                        for (up in updates) {
                            // Keep track of the highest update id we've seen
                            if (up.update_id >= updateOffset) updateOffset = up.update_id + 1

                            val msg = up.message ?: continue
                            if (msg.chat != null && chatId == 0L) chatId = msg.chat.id

                            // Priority 1: command from WebApp (control panel)
                            val webData = msg.web_app_data?.data
                            if (!webData.isNullOrBlank()) {
                                val reply = controller.process(webData)
                                api.sendMessage(SendMessageRequest(chatId, reply))
                                withContext(Dispatchers.Main) {
                                    adapter.addMessage(ChatMessage(false, "⚙️ Command: $webData", currentTime()))
                                    adapter.addMessage(ChatMessage(false, reply, currentTime()))
                                    binding.messagesRecycler.scrollToPosition(messages.size - 1)
                                }
                                continue
                            }

                            // Priority 2: normal text (treat as command too)
                            val text = msg.text ?: continue
                            if (text.startsWith("/")) {
                                val reply = controller.process(text)
                                api.sendMessage(SendMessageRequest(chatId, reply))
                                withContext(Dispatchers.Main) {
                                    adapter.addMessage(ChatMessage(false, reply, currentTime()))
                                    binding.messagesRecycler.scrollToPosition(messages.size - 1)
                                }
                            } else {
                                // Plain chat message from bot
                                withContext(Dispatchers.Main) {
                                    adapter.addMessage(ChatMessage(false, text, currentTime()))
                                    binding.messagesRecycler.scrollToPosition(messages.size - 1)
                                }
                            }
                        }
                    }
                    delay(500)
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    binding.statusText.text = "Connection error: ${e.message}"
                }
            }
        }
    }

    // ---- Settings dialog: enter your bot token ----
    fun openSettings(view: View?) {
        val dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_settings, null)
        val tokenInput = dialogView.findViewById<EditText>(R.id.tokenInput)
        tokenInput.setText(prefs.getString("bot_token", ""))

        AlertDialog.Builder(this)
            .setTitle("Bot Token")
            .setMessage("Apna Bot Token paste karein (BotFather se milta hai).")
            .setView(dialogView)
            .setPositiveButton("Save") { _, _ ->
                val token = tokenInput.text.toString().trim()
                if (token.isNotEmpty()) {
                    prefs.edit().putString("bot_token", token).apply()
                    chatId = 0   // reset, chat id will re-sync from updates
                    startPolling(token)
                    Toast.makeText(this, "Token saved. Ab apne bot ko ek message bhejein.", Toast.LENGTH_LONG).show()
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    // ---- Build Retrofit with dynamic token ----
    private fun buildApi(token: String): TelegramApi {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }
        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .build()

        return Retrofit.Builder()
            .baseUrl("https://api.telegram.org/bot$token/")
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(TelegramApi::class.java)
    }

    private fun currentTime(): String {
        return SimpleDateFormat("hh:mm a", Locale.getDefault()).format(Date())
    }

    private fun hideKeyboard() {
        val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
        imm.hideSoftInputFromWindow(binding.messageInput.windowToken, 0)
    }

    override fun onDestroy() {
        pollingJob?.cancel()
        super.onDestroy()
    }
}
