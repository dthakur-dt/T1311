package com.example.telegrambotapp

/**
 * Data models for Telegram Bot API responses.
 * Only the fields we need are mapped (Gson ignores the rest).
 */

// One chat message shown in the RecyclerView
data class ChatMessage(
    val isFromUser: Boolean,
    val text: String,
    val time: String
)

// ---- sendMessage request ----
data class SendMessageRequest(
    val chat_id: Long,
    val text: String
)

data class SendMessageResponse(
    val ok: Boolean,
    val description: String? = null
)

// ---- getUpdates response ----
data class GetUpdatesResponse(
    val ok: Boolean,
    val result: List<Update> = emptyList()
)

data class Update(
    val update_id: Long,
    val message: TgMessage? = null
)

data class TgMessage(
    val message_id: Long,
    val text: String? = null,
    val chat: TgChat? = null,
    val date: Long = 0,
    val web_app_data: WebAppData? = null
)

// Data sent from a Telegram WebApp via WebApp.sendData()
data class WebAppData(
    val data: String
)

data class TgChat(
    val id: Long
)
