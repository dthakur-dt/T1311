package com.example.telegrambotapp.ui.home

import android.content.Context
import android.content.SharedPreferences
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.example.telegrambotapp.databinding.FragmentHomeBinding

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val prefs: SharedPreferences =
            requireContext().getSharedPreferences("telegram_bot", Context.MODE_PRIVATE)
        val mobile = prefs.getString("mobile_number", "")
        if (mobile.isNullOrEmpty()) {
            binding.statusText.text = "⚠️ Mobile number set nahi hai"
            binding.deviceNumber.text = "Settings tab me mobile number daalein"
        } else {
            binding.statusText.text = "✅ Bot connected · LIVE"
            binding.deviceNumber.text = "Device: $mobile"
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
