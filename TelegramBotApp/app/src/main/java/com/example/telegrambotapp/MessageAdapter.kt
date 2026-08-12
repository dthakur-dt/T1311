package com.example.telegrambotapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

/**
 * RecyclerView adapter that shows the chat messages with
 * different bubble styles for user vs. bot messages.
 */
class MessageAdapter(private val messages: MutableList<ChatMessage>) :
    RecyclerView.Adapter<MessageAdapter.MessageViewHolder>() {

    class MessageViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val bubble: TextView = view.findViewById(R.id.messageBubble)
        val time: TextView = view.findViewById(R.id.messageTime)
        val row: LinearLayout = view.findViewById(R.id.messageRow)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MessageViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_message, parent, false)
        return MessageViewHolder(view)
    }

    override fun onBindViewHolder(holder: MessageViewHolder, position: Int) {
        val msg = messages[position]
        holder.bubble.text = msg.text
        holder.time.text = msg.time

        val params = holder.bubble.layoutParams as LinearLayout.LayoutParams
        if (msg.isFromUser) {
            // User message -> right aligned, light blue bubble
            holder.bubble.setBackgroundResource(R.drawable.bg_message_user)
            holder.bubble.setTextColor(holder.itemView.context.getColor(R.color.black))
            params.gravity = android.view.Gravity.END
            holder.time.gravity = android.view.Gravity.END
        } else {
            // Bot message -> left aligned, telegram blue bubble
            holder.bubble.setBackgroundResource(R.drawable.bg_message_bot)
            holder.bubble.setTextColor(holder.itemView.context.getColor(R.color.white))
            params.gravity = android.view.Gravity.START
            holder.time.gravity = android.view.Gravity.START
        }
        holder.bubble.layoutParams = params
    }

    override fun getItemCount(): Int = messages.size

    // Append a message and auto-scroll (call from main thread)
    fun addMessage(msg: ChatMessage) {
        messages.add(msg)
        notifyItemInserted(messages.size - 1)
    }
}
