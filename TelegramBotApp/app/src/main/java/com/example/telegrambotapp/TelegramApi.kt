package com.example.telegrambotapp

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

/**
 * Retrofit interface for the Telegram Bot API.
 * The base URL is set dynamically to "https://api.telegram.org/bot<TOKEN>/"
 */
interface TelegramApi {

    @POST("sendMessage")
    suspend fun sendMessage(@Body body: SendMessageRequest): Response<SendMessageResponse>

    @GET("getUpdates")
    suspend fun getUpdates(
        @Query("offset") offset: Long,
        @Query("timeout") timeout: Int = 5
    ): Response<GetUpdatesResponse>
}
