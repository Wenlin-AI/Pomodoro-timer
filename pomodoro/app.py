"""Application entry point for the Pomodoro Timer."""
import os
import sys
import logging
import importlib.resources
import shutil
from PyQt6.QtWidgets import QApplication

try:
    import appdirs
    user_data_dir = appdirs.user_data_dir("pomodoro-timer", "pomodoro")
    os.makedirs(user_data_dir, exist_ok=True)
    log_file = os.path.join(user_data_dir, "pomodoro.log")
except ImportError:
    user_data_dir = os.path.expanduser("~/.pomodoro-timer")
    os.makedirs(user_data_dir, exist_ok=True)
    log_file = os.path.join(user_data_dir, "pomodoro.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main(focus=None, rest=None):
    """Launch the Pomodoro Timer application.

    Parameters
    ----------
    focus : int | None
        Override focus period duration in minutes.
    rest : int | None
        Override rest period duration in minutes.
    """
    try:
        from .config import Config
        from .sound import SoundManager
        from .notes import NotesManager
        from .session import SessionManager
        from .ui import PomodoroTimer
        from .utils import get_resource_path

        try:
            import appdirs
            user_config_dir = appdirs.user_config_dir("pomodoro-timer", "pomodoro")
        except ImportError:
            user_config_dir = os.path.expanduser("~/.pomodoro-timer/config")
        
        os.makedirs(user_config_dir, exist_ok=True)
        
        # User config file path
        user_config_path = os.path.join(user_config_dir, "config.json")
        
        # Default config file path (in package)
        default_config_path = get_resource_path("config.json")
        
        # If user config doesn't exist, but default does, copy it
        if not os.path.exists(user_config_path) and os.path.exists(default_config_path):
            shutil.copy2(default_config_path, user_config_path)
        
        # Use user config if it exists, otherwise fall back to package config
        config_path = user_config_path if os.path.exists(user_config_path) else default_config_path
        config = Config(config_path)

        if focus is not None:
            config.config["timer"]["focus_period_minutes"] = focus
        if rest is not None:
            config.config["timer"]["rest_period_minutes"] = rest

        sound_manager = SoundManager(config)
        notes_manager = NotesManager(config)
        session_manager = SessionManager(config, notes_manager, os.path.join(user_data_dir, "pomodoro_sessions.log"))

        app = QApplication(sys.argv)
        app.setApplicationName("Pomodoro Timer")

        # Make sure icon and sound directories exist in the user data directory
        user_icons_dir = os.path.join(user_data_dir, "icons")
        os.makedirs(user_icons_dir, exist_ok=True)
        
        user_sounds_dir = os.path.join(user_data_dir, "sounds")
        os.makedirs(user_sounds_dir, exist_ok=True)
        
        # Copy default resources to user directory if they don't exist
        for resource_dir, user_dir in [("icons", user_icons_dir), ("sounds", user_sounds_dir)]:
            pkg_resource_dir = get_resource_path(resource_dir)
            if os.path.exists(pkg_resource_dir) and os.path.isdir(pkg_resource_dir):
                for filename in os.listdir(pkg_resource_dir):
                    src_path = os.path.join(pkg_resource_dir, filename)
                    dst_path = os.path.join(user_dir, filename)
                    if not os.path.exists(dst_path) and os.path.isfile(src_path):
                        shutil.copy2(src_path, dst_path)

        window = PomodoroTimer(config, sound_manager, notes_manager, session_manager)
        window.show()

        sys.exit(app.exec())
    except Exception as e:
        logger.exception(f"Application error: {e}")
        sys.exit(1)
