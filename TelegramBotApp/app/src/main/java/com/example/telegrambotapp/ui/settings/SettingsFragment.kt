package com.example.telegrambotapp.ui.settings

import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.example.telegrambotapp.databinding.FragmentSettingsBinding
import com.example.telegrambotapp.HeartbeatManager

class SettingsFragment : Fragment() {

    private var _binding: FragmentSettingsBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentSettingsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val prefs = requireContext().getSharedPreferences("telegram_bot", Context.MODE_PRIVATE)

        // Load saved values
        binding.tokenInput.setText(prefs.getString("bot_token", ""))
        binding.mobileInput.setText(prefs.getString("mobile_number", ""))

        binding.saveButton.setOnClickListener {
            val token = binding.tokenInput.text.toString().trim()
            val mobile = binding.mobileInput.text.toString().trim()

            if (token.isEmpty()) {
                Toast.makeText(requireContext(), "Token daalein pehle", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (!mobile.matches(Regex("\\d{10}"))) {
                Toast.makeText(requireContext(), "Sahi 10-digit mobile number daalein", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            prefs.edit()
                .putString("bot_token", token)
                .putString("mobile_number", mobile)
                .apply()

            // Heartbeat shuru karo (ya naya number set hone par restart)
            HeartbeatManager(requireContext()).start()

            Toast.makeText(requireContext(), "Sab save ho gaya", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
