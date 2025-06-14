"""Application entry point for the Pomodoro Timer."""
import os
import sys
import logging
from PyQt6.QtWidgets import QApplication

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pomodoro.log"),
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

        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")
        config_path = os.path.normpath(config_path)
        config = Config(config_path)

        if focus is not None:
            config.config["timer"]["focus_period_minutes"] = focus
        if rest is not None:
            config.config["timer"]["rest_period_minutes"] = rest

        sound_manager = SoundManager(config)
        notes_manager = NotesManager(config)
        session_manager = SessionManager()

        app = QApplication(sys.argv)
        app.setApplicationName("Pomodoro Timer")

        icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons")
        icons_dir = os.path.normpath(icons_dir)
        if not os.path.exists(icons_dir):
            os.makedirs(icons_dir)

        sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sounds")
        sounds_dir = os.path.normpath(sounds_dir)
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir)

        window = PomodoroTimer(config, sound_manager, notes_manager, session_manager)
        window.show()

        sys.exit(app.exec())
    except Exception as e:
        logger.exception(f"Application error: {e}")
        sys.exit(1)
