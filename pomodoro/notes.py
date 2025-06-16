"""
Notes integration module for the Pomodoro Timer application.
Handles integration with Obsidian and other note-taking systems.
"""
import webbrowser
import datetime
import logging
import urllib.parse
import requests

logger = logging.getLogger(__name__)

class NotesManager:
    """Manager for integrating with note-taking systems."""

    def __init__(self, config):
        """
        Initialize the notes manager.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.enabled = config.is_obsidian_enabled()
        self.obsidian_settings = config.get_obsidian_settings()

    def is_enabled(self):
        """Check if note-taking integration is enabled."""
        return self.enabled

    def open_daily_note(self):
        """Open today's daily note in Obsidian."""
        if not self.enabled:
            logger.info("Notes integration is disabled")
            return False
            
        try:
            vault = self.obsidian_settings["vault_name"]
            path = self.obsidian_settings["daily_notes_path"]
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Construct the URL with proper encoding
            file_path = f"{path}/{date_str}"
            encoded_path = urllib.parse.quote(file_path)
            url = f"obsidian://open?vault={vault}&file={encoded_path}"
            
            webbrowser.open(url)
            logger.info(f"Opened daily note for {date_str}")
            return True
        except Exception as e:
            logger.error(f"Error opening daily note: {e}")
            return False

    def open_weekly_note(self):
        """Open this week's weekly note in Obsidian."""
        if not self.enabled:
            logger.info("Notes integration is disabled")
            return False
            
        try:
            vault = self.obsidian_settings["vault_name"]
            path = self.obsidian_settings["weekly_notes_path"]
            
            # Week note format: YYYY-WXX where XX is the week number
            week_str = datetime.datetime.now().strftime("%Y-W%V")
            
            # Construct the URL with proper encoding
            file_path = f"{path}/{week_str}"
            encoded_path = urllib.parse.quote(file_path)
            url = f"obsidian://open?vault={vault}&file={encoded_path}"
            
            webbrowser.open(url)
            logger.info(f"Opened weekly note for {week_str}")
            return True
        except Exception as e:
            logger.error(f"Error opening weekly note: {e}")
            return False

    def log_focus_session(self, start, end, focus_text, duration, status):
        """Record a focus session to Obsidian via the REST API."""
        if not self.enabled:
            return False

        api = self.obsidian_settings.get("rest_api", {})
        endpoint = api.get("endpoint", "https://localhost")
        port = api.get("port", 27123)
        api_key = api.get("api_key", "")
        folder = api.get("log_folder", "Focus Logs")

        date_str = start.strftime("%Y-%m-%d")
        filename = f"{date_str} - Focus sessions.md"
        file_path = f"{folder}/{filename}" if folder else filename

        base_url = f"{endpoint}:{port}/vault/{urllib.parse.quote(file_path)}"
        headers = {"Authorization": api_key, "Content-Type": "text/markdown"}

        try:
            response = requests.get(base_url, headers=headers, verify=False)
            if response.status_code == 404:
                header = "| Start | End | Focus | Duration | Status |\n| --- | --- | --- | --- | --- |\n"
                requests.put(base_url, data=header.encode("utf-8"), headers=headers, verify=False)

            row = f"| {start.strftime('%H:%M:%S')} | {end.strftime('%H:%M:%S')} | {focus_text or '-'} | {int(duration)}s | {status} |\n"
            requests.post(base_url, data=row.encode("utf-8"), headers=headers, verify=False)
            return True
        except Exception as e:
            logger.error(f"Error logging session to Obsidian: {e}")
            return False
