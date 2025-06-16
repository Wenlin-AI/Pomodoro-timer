"""
Configuration module for the Pomodoro Timer application.
Handles loading, parsing, and accessing configuration values.
"""
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "timer": {
        "focus_period_minutes": 25,
        "rest_period_minutes": 5
    },
    "sounds": {
        "focus_end": {
            "file": "sounds/focus_end.mp3",
            "volume": 0.5
        },
        "rest_end": {
            "file": "sounds/rest_end.mp3",
            "volume": 0.8
        }
    },
    "obsidian": {
        "enabled": True,
        "vault_name": "memory",
        "daily_notes_path": "Personal/Notes/Daily Notes",
        "weekly_notes_path": "Personal/Notes/Weekly Notes",
        "rest_api": {
            "api_key": "",
            "endpoint": "https://localhost",
            "port": 27123,
            "log_folder": "Focus Logs"
        }
    },
    "ui": {
        "show_focus_text": True,
        "always_on_top": True,
        "start_position": {
            "x": 100,
            "y": 100
        },
        "window_size": {
            "width": 300,
            "height": 300
        }
    }
}

class Config:
    """Configuration manager for the Pomodoro Timer application."""

    def __init__(self, config_path="config.json"):
        """Initialize the configuration manager."""
        self.config_path = config_path
        self.config = self._load_config()
        self._batch_mode = False

    def _load_config(self):
        """Load configuration from file or create default if not exists."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    config = json.load(file)
                    # Ensure all default keys exist
                    self._ensure_defaults(config)
                    return config
            else:
                # Create default configuration file if not exists
                with open(self.config_path, 'w') as file:
                    json.dump(DEFAULT_CONFIG, file, indent=2)
                logger.info(f"Created default configuration file: {self.config_path}")
                return DEFAULT_CONFIG
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return DEFAULT_CONFIG

    def _ensure_defaults(self, config):
        """Ensure all default keys exist in the configuration."""
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in config[key]:
                        config[key][sub_key] = sub_value
    
    def start_batch(self):
        """Start batching configuration changes."""
        self._batch_mode = True
    
    def end_batch(self):
        """End batching configuration changes and save."""
        self._batch_mode = False
        self.save()

    def save(self):
        """Save current configuration to file."""
        if self._batch_mode:
            return  # Skip saving in batch mode
            
        try:
            with open(self.config_path, 'w') as file:
                json.dump(self.config, file, indent=2)
            logger.info(f"Configuration saved to: {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def get_focus_period(self):
        """Get the focus period duration in minutes."""
        return self.config["timer"]["focus_period_minutes"]

    def get_rest_period(self):
        """Get the rest period duration in minutes."""
        return self.config["timer"]["rest_period_minutes"]

    def get_focus_sound(self):
        """Get the focus end sound file path."""
        return self.config["sounds"]["focus_end"]["file"]

    def get_focus_volume(self):
        """Get the focus end sound volume."""
        return self.config["sounds"]["focus_end"]["volume"]

    def get_rest_sound(self):
        """Get the rest end sound file path."""
        return self.config["sounds"]["rest_end"]["file"]

    def get_rest_volume(self):
        """Get the rest end sound volume."""
        return self.config["sounds"]["rest_end"]["volume"]

    def is_obsidian_enabled(self):
        """Check if Obsidian integration is enabled."""
        return self.config["obsidian"]["enabled"]

    def get_obsidian_settings(self):
        """Get the Obsidian settings."""
        return self.config["obsidian"]

    def get_ui_settings(self):
        """Get the UI settings."""
        return self.config["ui"]

    def set_focus_period(self, minutes):
        """Set the focus period duration in minutes."""
        self.config["timer"]["focus_period_minutes"] = minutes
        self.save()

    def set_rest_period(self, minutes):
        """Set the rest period duration in minutes."""
        self.config["timer"]["rest_period_minutes"] = minutes
        self.save()

    def set_sound_settings(self, sound_type, file_path=None, volume=None):
        """Set sound settings for a specific type (focus_end or rest_end)."""
        if sound_type not in ["focus_end", "rest_end"]:
            raise ValueError("sound_type must be 'focus_end' or 'rest_end'")

        if file_path:
            self.config["sounds"][sound_type]["file"] = file_path
        if volume is not None:
            self.config["sounds"][sound_type]["volume"] = max(0.0, min(1.0, volume))
        self.save()

    def set_obsidian_enabled(self, enabled):
        """Set whether Obsidian integration is enabled."""
        self.config["obsidian"]["enabled"] = enabled
        self.save()

    def update_obsidian_settings(self, vault_name=None, daily_path=None, weekly_path=None):
        """Update Obsidian settings."""
        if vault_name:
            self.config["obsidian"]["vault_name"] = vault_name
        if daily_path:
            self.config["obsidian"]["daily_notes_path"] = daily_path
        if weekly_path:
            self.config["obsidian"]["weekly_notes_path"] = weekly_path
        self.save()

    def get_rest_api_settings(self):
        """Get Obsidian REST API settings."""
        return self.config["obsidian"].get("rest_api", {})

    def update_rest_api_settings(self, api_key=None, endpoint=None, port=None, log_folder=None):
        """Update REST API configuration."""
        rest_api = self.config["obsidian"].setdefault("rest_api", {})
        if api_key is not None:
            rest_api["api_key"] = api_key
        if endpoint is not None:
            rest_api["endpoint"] = endpoint
        if port is not None:
            rest_api["port"] = port
        if log_folder is not None:
            rest_api["log_folder"] = log_folder
        self.save()
