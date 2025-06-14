"""Command-line interface for the Pomodoro Timer."""
from __future__ import annotations

import argparse
import importlib.metadata

from .app import main as run_app


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return the parsed CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="pomodoro",
        description="Launch the Pomodoro Timer application",
    )
    parser.add_argument(
        "--focus",
        type=int,
        metavar="MINUTES",
        help="Focus period duration in minutes",
    )
    parser.add_argument(
        "--rest",
        type=int,
        metavar="MINUTES",
        help="Rest period duration in minutes",
    )

    try:
        pkg_version = importlib.metadata.version("pomodoro-timer")
    except importlib.metadata.PackageNotFoundError:
        pkg_version = "unknown"

    parser.add_argument(
        "--version",
        action="version",
        version=f"pomodoro {pkg_version}",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    run_app(focus=args.focus, rest=args.rest)


if __name__ == "__main__":
    main()
