package com.example.telegrambotapp.ui.controls

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.example.telegrambotapp.AppController
import com.example.telegrambotapp.databinding.FragmentControlsBinding
import kotlinx.coroutines.*

/**
 * Controls tab — Light / Fan / DND / Dark Mode toggles.
 * Har toggle AppController se device state ko control karta hai.
 */
class ControlsFragment : Fragment() {

    private var _binding: FragmentControlsBinding? = null
    private val binding get() = _binding!!
    private lateinit var controller: AppController
    private var initialized = false

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentControlsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        controller = AppController(requireContext())

        // Load saved states without firing listeners
        initialized = false
        binding.lightSwitch.isChecked = controller.isOn("light")
        binding.fanSwitch.isChecked = controller.isOn("fan")
        binding.dndSwitch.isChecked = controller.isOn("dnd")
        binding.darkSwitch.isChecked = controller.isOn("dark")
        initialized = true

        binding.lightSwitch.setOnCheckedChangeListener { _, on -> onToggle("TOGGLE_LIGHT", on) }
        binding.fanSwitch.setOnCheckedChangeListener { _, on -> onToggle("TOGGLE_FAN", on) }
        binding.dndSwitch.setOnCheckedChangeListener { _, on -> onToggle("TOGGLE_DND", on) }
        binding.darkSwitch.setOnCheckedChangeListener { _, on -> onToggle("TOGGLE_DARK", on) }
    }

    private fun onToggle(cmd: String, on: Boolean) {
        if (!initialized) return
        // AppController.process cmd returns reply string; state already applied
        val reply = controller.process(cmd)
        Toast.makeText(requireContext(), reply, Toast.LENGTH_SHORT).show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
