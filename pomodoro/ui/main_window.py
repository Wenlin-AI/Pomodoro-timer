"""
Main window component for the Pomodoro Timer application.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QInputDialog, QApplication
)
from PyQt6.QtCore import QTimer, Qt, QPoint, QRect
from PyQt6.QtGui import QIcon, QMouseEvent

from .config_dialog import PomodoroConfigDialog
from .components import TimerLabel, FocusLabel, PomodoroButton

logger = logging.getLogger(__name__)

class PomodoroTimer(QWidget):
    """Main window for the Pomodoro Timer application."""

    def __init__(self, config, sound_manager, notes_manager, session_manager):
        """
        Initialize the main window.
        
        Args:
            config: Application configuration
            sound_manager: Sound manager instance
            notes_manager: Notes manager instance
            session_manager: Session manager instance
        """
        super().__init__()

        self.config = config
        self.sound_manager = sound_manager
        self.notes_manager = notes_manager
        self.session_manager = session_manager
        
        # Set up timer settings from config
        self.pomodoro_time = config.get_focus_period() * 60  # minutes to seconds
        self.rest_time = config.get_rest_period() * 60  # minutes to seconds
        self.time_left = self.pomodoro_time
          # State variables
        self.running = False
        self.is_rest_period = False
        self.dragging = False
        self.resizing = False
        self.focus_text = ""
        self.drag_start_position = QPoint(0, 0)
        self.resize_start_position = QPoint(0, 0)
        self.original_geometry = QRect(0, 0, 0, 0)
        
        self.initUI()

    def initUI(self):
        """Initialize the user interface."""
        self.setWindowTitle("")  # Remove application name from title bar
        
        ui_settings = self.config.get_ui_settings()
        pos = ui_settings.get("start_position", {"x": 100, "y": 100})
        size = ui_settings.get("window_size", {"width": 300, "height": 300})
        
        self.setGeometry(pos["x"], pos["y"], size["width"], size["height"])
        self.setMinimumSize(200, 200)  # Set minimum size for the window
        
        window_flags = Qt.WindowType.FramelessWindowHint
        if ui_settings.get("always_on_top", True):
            window_flags |= Qt.WindowType.WindowStaysOnTopHint
        
        self.setWindowFlags(window_flags)        # Set a custom icon as the application icon
        from ..utils import get_resource_path
        icon_path = get_resource_path("icons/pomodoro.png")
        self.setWindowIcon(QIcon(icon_path))

        # Create the layouts and widgets
        self._create_layout()
        
        # Set up the timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def _create_layout(self):
        """Create the main layout and widgets."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(2)        # Focus text label
        self.focus_label = FocusLabel("", self)
        main_layout.addWidget(self.focus_label)

        # Timer display
        self.timer_label = TimerLabel(f"{self.config.get_focus_period():02d}:00", self)
        main_layout.addWidget(self.timer_label)

        # Button grid
        self.grid_layout = QGridLayout()
        self._create_buttons()
        main_layout.addLayout(self.grid_layout)
        
        self.setLayout(main_layout)

    def _create_buttons(self):
        """Create and layout the buttons."""        # Focus button
        self.focus_button = PomodoroButton("Focus", self)
        self.focus_button.clicked.connect(self.start_focus)
        self.grid_layout.addWidget(self.focus_button, 0, 0)

        # Rest button
        self.rest_button = PomodoroButton("Rest", self)
        self.rest_button.clicked.connect(self.start_rest)
        self.grid_layout.addWidget(self.rest_button, 0, 1)

        # Pause button
        self.pause_button = PomodoroButton("Pause", self)
        self.pause_button.clicked.connect(self.pause_timer)
        self.grid_layout.addWidget(self.pause_button, 1, 0)

        # Settings button
        self.settings_button = PomodoroButton("Settings", self)
        self.settings_button.clicked.connect(self.open_settings)
        self.grid_layout.addWidget(self.settings_button, 1, 1)        # Add note buttons only if obsidian is enabled
        self.obsidian_row = None
        if self.notes_manager.is_enabled():
            # Daily button
            self.daily_button = PomodoroButton("Daily", self)
            self.daily_button.clicked.connect(self.notes_manager.open_daily_note)
            self.grid_layout.addWidget(self.daily_button, 2, 0)

            # Weekly button
            self.weekly_button = PomodoroButton("Weekly", self)
            self.weekly_button.clicked.connect(self.notes_manager.open_weekly_note)
            self.grid_layout.addWidget(self.weekly_button, 2, 1)
            self.obsidian_row = 2

        # Exit button
        self.exit_button = PomodoroButton("Exit", self)
        self.exit_button.clicked.connect(self.close)
        row = 3 if self.notes_manager.is_enabled() else 2
        self.grid_layout.addWidget(self.exit_button, row, 0, 1, 2)  # span both columns
    
    def mousePressEvent(self, a0: QMouseEvent | None):
        """Handle mouse press events for dragging and resizing."""
        if a0 and a0.button() == Qt.MouseButton.LeftButton:
            if QApplication.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
                self.resizing = True
                self.resize_start_position = a0.globalPosition().toPoint()
                self.original_geometry = self.geometry()
            else:
                self.dragging = True
                self.drag_start_position = a0.globalPosition().toPoint() - self.frameGeometry().topLeft()
            a0.accept()
            
    def mouseMoveEvent(self, a0: QMouseEvent | None):
        """Handle mouse move events for dragging and resizing."""
        if a0:
            if self.dragging:
                self.move(a0.globalPosition().toPoint() - self.drag_start_position)
                a0.accept()
            elif self.resizing:
                self.resize_window(a0.globalPosition().toPoint())
                a0.accept()
                
    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        """Handle mouse release events to end dragging and resizing."""
        if a0 and a0.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            
            # Save the new position and size in the config
            ui_settings = self.config.get_ui_settings()
            ui_settings["start_position"]["x"] = self.x()
            ui_settings["start_position"]["y"] = self.y()
            ui_settings["window_size"]["width"] = self.width()
            ui_settings["window_size"]["height"] = self.height()
            
            a0.accept()

    def resize_window(self, global_pos):
        """Resize the window based on mouse movement."""
        delta = global_pos - self.resize_start_position
        new_width = max(self.minimumWidth(), self.original_geometry.width() + delta.x())
        new_height = max(self.minimumHeight(), self.original_geometry.height() + delta.y())
        self.setGeometry(
            self.original_geometry.x(),
            self.original_geometry.y(),
            new_width,
            new_height
        )

    def start_focus(self):
        """Start a focus session."""
        text, ok = QInputDialog.getText(self, 'Focus Session', 'What are you focusing on?')
        if ok:
            self.focus_text = text
            self.update_focus_label()
            self.session_manager.start_session(self.focus_text)
            self.time_left = self.pomodoro_time
            self.is_rest_period = False
            self.start_timer()

    def start_rest(self):
        """Start a rest session."""
        if self.running and not self.is_rest_period:
            self.session_manager.fail()
        self.focus_text = ""
        self.focus_label.setText("")
        self.time_left = self.rest_time
        self.is_rest_period = True
        self.start_timer()

    def start_timer(self):
        """Start the timer."""
        if not self.running:
            self.running = True
            self.timer.start(1000)  # Update every second
            self.pause_button.setText("Pause")

    def pause_timer(self):
        """Pause or resume the timer."""
        if self.running:
            self.running = False
            self.timer.stop()
            if not self.is_rest_period:
                self.session_manager.pause()
            self.pause_button.setText("Continue")
        else:
            self.running = True
            self.timer.start(1000)
            if not self.is_rest_period:
                self.session_manager.resume()
            self.pause_button.setText("Pause")

    def update_timer(self):
        """Update the timer display and handle timer completion."""
        if self.running:
            mins, secs = divmod(self.time_left, 60)
            self.timer_label.setText(f"{mins:02d}:{secs:02d}")
            
            if self.time_left > 0:
                self.time_left -= 1
            else:
                self.running = False
                self.timer.stop()
                
                if not self.is_rest_period:
                    # Focus period ended
                    self.sound_manager.play_focus_end()
                    self.session_manager.complete()
                    self.start_rest_period()
                else:
                    # Rest period ended
                    self.sound_manager.play_rest_end()
                    self.reset_timer()

    def start_rest_period(self):
        """Start the rest period after a focus period."""
        self.is_rest_period = True
        self.time_left = self.rest_time
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.setText(f"{mins:02d}:{secs:02d}")
        self.running = True
        self.timer.start(1000)

    def reset_timer(self):
        """Reset the timer to initial state."""
        self.running = False
        self.timer.stop()
        self.time_left = self.pomodoro_time if not self.is_rest_period else self.rest_time
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.setText(f"{mins:02d}:{secs:02d}")
        self.pause_button.setText("Pause")

    def update_focus_label(self):
        """Update the focus text label."""
        if self.focus_text:
            self.focus_label.setText(f"Focus: {self.focus_text}")
        else:
            self.focus_label.setText("")

    def open_settings(self):
        """Open the settings dialog."""
        dialog = PomodoroConfigDialog(self.config, self)
        if dialog.exec():
            # Update timer values from config
            self.pomodoro_time = self.config.get_focus_period() * 60
            self.rest_time = self.config.get_rest_period() * 60
            
            # Reset timer display if not running
            if not self.running:
                self.time_left = self.pomodoro_time if not self.is_rest_period else self.rest_time
                mins, secs = divmod(self.time_left, 60)
                self.timer_label.setText(f"{mins:02d}:{secs:02d}")
            
            # Update notes manager enabled state
            if self.notes_manager.enabled != self.config.is_obsidian_enabled():
                self.notes_manager.enabled = self.config.is_obsidian_enabled()
                # Restart the application to apply the changes
                self.close()
                app = QApplication.instance()
                if app:
                    app.quit()  # Exit with restart code

    def closeEvent(self, event):
        """Handle window close events."""
        if self.running and not self.is_rest_period:
            self.session_manager.fail()
        event.accept()
