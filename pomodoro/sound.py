"""
Sound management module for the Pomodoro Timer application.
Handles loading and playing sound files with volume control.
"""
import os
import logging

# Suppress the default pygame support message
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

logger = logging.getLogger(__name__)

class SoundManager:
    """Manager for playing application sounds with volume control."""

    def __init__(self, config):
        """Initialize the sound manager."""
        self.config = config
        self._init_mixer()

    def _init_mixer(self):
        """Initialize the pygame mixer."""
        try:
            pygame.mixer.init()
            logger.info("Sound system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize sound system: {e}")

    def play_focus_end(self):
        """Play the focus end sound."""
        sound_file = self.config.get_focus_sound()
        volume = self.config.get_focus_volume()
        self._play_sound(sound_file, volume)

    def play_rest_end(self):
        """Play the rest end sound."""
        sound_file = self.config.get_rest_sound()
        volume = self.config.get_rest_volume()
        self._play_sound(sound_file, volume)

    def _play_sound(self, sound_file, volume):
        """
        Play a sound file with the specified volume.
        
        Args:
            sound_file: Path to the sound file
            volume: Volume level (0.0 to 1.0)
        """
        try:
            if not os.path.exists(sound_file):
                logger.warning(f"Sound file not found: {sound_file}")
                return
                
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()
            logger.debug(f"Playing sound: {sound_file} at volume: {volume}")
        except Exception as e:
            logger.error(f"Error playing sound {sound_file}: {e}")
