"""Session management for Pomodoro Timer with optional Obsidian logging."""

from __future__ import annotations

import datetime
import logging
import os
from typing import List, Tuple

logger = logging.getLogger(__name__)


class SessionManager:
    """Track focus sessions and log them to a file or to Obsidian."""

    def __init__(self, config, notes_manager, log_file: str | None = None):
        self.config = config
        self.notes_manager = notes_manager
        self.log_file = log_file or "pomodoro_sessions.log"

        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        self.session_count = self._get_session_count()
        self.current_session: dict | None = None

    def _get_session_count(self) -> int:
        try:
            if not os.path.exists(self.log_file):
                return 0
            with open(self.log_file, "r") as file:
                return sum(1 for line in file if line.startswith("|") and "completed" in line)
        except Exception as exc:
            logger.error(f"Error reading session count: {exc}")
            return 0

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------
    def start_session(self, focus_text: str) -> None:
        """Start a focus session."""
        self.current_session = {
            "focus": focus_text,
            "start": datetime.datetime.now(),
            "pauses": [],  # type: List[Tuple[datetime.datetime, datetime.datetime]]
            "paused_since": None,
        }

    def pause(self) -> None:
        if self.current_session and self.current_session["paused_since"] is None:
            self.current_session["paused_since"] = datetime.datetime.now()

    def resume(self) -> None:
        if self.current_session and self.current_session["paused_since"] is not None:
            start = self.current_session["paused_since"]
            self.current_session["pauses"].append((start, datetime.datetime.now()))
            self.current_session["paused_since"] = None

    def complete(self) -> None:
        if not self.current_session:
            return
        if self.current_session.get("paused_since"):
            start = self.current_session["paused_since"]
            self.current_session["pauses"].append((start, datetime.datetime.now()))
            self.current_session["paused_since"] = None
        self.current_session["end"] = datetime.datetime.now()
        self._finalize_session("completed")

    def fail(self) -> None:
        if not self.current_session:
            return
        if self.current_session.get("paused_since"):
            start = self.current_session["paused_since"]
            self.current_session["pauses"].append((start, datetime.datetime.now()))
            self.current_session["paused_since"] = None
        self.current_session["end"] = datetime.datetime.now()
        self._finalize_session("failed")

    def _finalize_session(self, status: str) -> None:
        session = self.current_session
        self.current_session = None
        if not session:
            return

        self.session_count += 1
        start = session["start"]
        end = session.get("end", datetime.datetime.now())
        pauses = session.get("pauses", [])
        paused_seconds = sum((b - a).total_seconds() for a, b in pauses)
        duration = (end - start).total_seconds() - paused_seconds
        focus = session.get("focus", "")

        if self.notes_manager.is_enabled():
            self.notes_manager.log_focus_session(start, end, focus, duration, status)
        else:
            self._log_to_file(start, end, focus, duration, status)

    # ------------------------------------------------------------------
    # Fallback file logging
    # ------------------------------------------------------------------
    def _log_to_file(self, start, end, focus, duration, status):
        try:
            header_needed = not os.path.exists(self.log_file)
            with open(self.log_file, "a") as file:
                if header_needed:
                    file.write("| Start | End | Focus | Duration | Status |\n")
                    file.write("| --- | --- | --- | --- | --- |\n")
                row = f"| {start.strftime('%Y-%m-%d %H:%M:%S')} | {end.strftime('%Y-%m-%d %H:%M:%S')} | {focus or '-'} | {int(duration)}s | {status} |\n"
                file.write(row)
        except Exception as exc:
            logger.error(f"Error logging session to file: {exc}")

