"""
Configuration dialog for the Pomodoro Timer.
"""
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout,
    QSpinBox, QDoubleSpinBox, QCheckBox, QDialogButtonBox,
    QLineEdit
)

logger = logging.getLogger(__name__)

class PomodoroConfigDialog(QDialog):
    """Dialog for configuring the Pomodoro Timer settings."""

    def __init__(self, config, parent=None):
        """
        Initialize the configuration dialog.
        
        Args:
            config: Application configuration
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        
        self.setWindowTitle("Pomodoro Settings")
        self.setMinimumWidth(350)
        
        self.tabs = QTabWidget()
        
        # Initialize UI components
        self._init_timer_tab()
        self._init_sounds_tab()
        self._init_notes_tab()
        
        # Add tabs to the tab widget
        self.tabs.addTab(self.timer_tab, "Timer")
        self.tabs.addTab(self.sounds_tab, "Sounds")
        self.tabs.addTab(self.notes_tab, "Notes")
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def _init_timer_tab(self):
        """Initialize the timer settings tab."""
        self.timer_tab = QWidget()
        timer_layout = QFormLayout()
        
        self.focus_spinbox = QSpinBox()
        self.focus_spinbox.setRange(1, 120)
        self.focus_spinbox.setValue(self.config.get_focus_period())
        self.focus_spinbox.setSuffix(" min")
        
        self.rest_spinbox = QSpinBox()
        self.rest_spinbox.setRange(1, 60)
        self.rest_spinbox.setValue(self.config.get_rest_period())
        self.rest_spinbox.setSuffix(" min")
        
        timer_layout.addRow("Focus period:", self.focus_spinbox)
        timer_layout.addRow("Rest period:", self.rest_spinbox)
        self.timer_tab.setLayout(timer_layout)

    def _init_sounds_tab(self):
        """Initialize the sounds settings tab."""
        self.sounds_tab = QWidget()
        sounds_layout = QFormLayout()
        
        # Focus sound volume
        self.focus_volume = QDoubleSpinBox()
        self.focus_volume.setRange(0, 1)
        self.focus_volume.setSingleStep(0.1)
        self.focus_volume.setDecimals(1)
        self.focus_volume.setValue(self.config.get_focus_volume())
        
        # Rest sound volume
        self.rest_volume = QDoubleSpinBox()
        self.rest_volume.setRange(0, 1)
        self.rest_volume.setSingleStep(0.1)
        self.rest_volume.setDecimals(1)
        self.rest_volume.setValue(self.config.get_rest_volume())
        
        sounds_layout.addRow("Focus end volume:", self.focus_volume)
        sounds_layout.addRow("Rest end volume:", self.rest_volume)
        self.sounds_tab.setLayout(sounds_layout)

    def _init_notes_tab(self):
        """Initialize the notes settings tab."""
        self.notes_tab = QWidget()
        notes_layout = QFormLayout()
        
        self.obsidian_enabled = QCheckBox()
        self.obsidian_enabled.setChecked(self.config.is_obsidian_enabled())

        obsidian_settings = self.config.get_obsidian_settings()
        rest_api = obsidian_settings.get("rest_api", {})

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setText(rest_api.get("api_key", ""))

        self.endpoint_edit = QLineEdit()
        self.endpoint_edit.setText(rest_api.get("endpoint", "https://localhost"))

        self.port_spinbox = QSpinBox()
        self.port_spinbox.setRange(1, 65535)
        self.port_spinbox.setValue(rest_api.get("port", 27123))

        self.folder_edit = QLineEdit()
        self.folder_edit.setText(rest_api.get("log_folder", "Focus Logs"))

        notes_layout.addRow("Enable Obsidian integration:", self.obsidian_enabled)
        notes_layout.addRow("API key:", self.api_key_edit)
        notes_layout.addRow("Endpoint:", self.endpoint_edit)
        notes_layout.addRow("Port:", self.port_spinbox)
        notes_layout.addRow("Log folder:", self.folder_edit)
        self.notes_tab.setLayout(notes_layout)

    def accept(self):
        """Save the configuration when the dialog is accepted."""
        # Start batch mode to prevent multiple saves
        self.config.start_batch()
        
        # Save timer settings
        self.config.set_focus_period(self.focus_spinbox.value())
        self.config.set_rest_period(self.rest_spinbox.value())
        
        # Save sound settings
        self.config.set_sound_settings("focus_end", volume=self.focus_volume.value())
        self.config.set_sound_settings("rest_end", volume=self.rest_volume.value())
        
        # Save obsidian settings
        self.config.set_obsidian_enabled(self.obsidian_enabled.isChecked())
        self.config.update_rest_api_settings(
            api_key=self.api_key_edit.text(),
            endpoint=self.endpoint_edit.text(),
            port=self.port_spinbox.value(),
            log_folder=self.folder_edit.text(),
        )
        
        # End batch mode and save all changes at once
        self.config.end_batch()
        
        super().accept()
