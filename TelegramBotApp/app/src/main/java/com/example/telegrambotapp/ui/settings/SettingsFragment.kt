package com.example.telegrambotapp.ui.settings

import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.example.telegrambotapp.databinding.FragmentSettingsBinding

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

        // Load saved token
        val prefs = requireContext().getSharedPreferences("telegram_bot", Context.MODE_PRIVATE)
        binding.tokenInput.setText(prefs.getString("bot_token", ""))

        binding.saveButton.setOnClickListener {
            val token = binding.tokenInput.text.toString().trim()
            if (token.isEmpty()) {
                Toast.makeText(requireContext(), "Token daalein pehle", Toast.LENGTH_SHORT).show()
            } else {
                prefs.edit().putString("bot_token", token).apply()
                Toast.makeText(requireContext(), "Token save ho gaya", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
