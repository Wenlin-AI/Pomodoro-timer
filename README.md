# Pomodoro Timer

A modern, customizable Pomodoro timer application built with Python and PyQt6.

## Overview

This Pomodoro Timer helps you boost productivity using the Pomodoro Technique — a time management method that uses a timer to break work into intervals, traditionally 25 minutes in length, separated by short breaks. This application provides a sleek, always-on-top interface to keep your focus sessions visible while working.

## Features

- **Pomodoro Sessions**: Configurable focus and rest periods (default 25/5 minutes)
- **Focus Tracking**: Enter what you're focusing on for each session
- **Session Logging**: Automatically logs completed sessions with timestamps
- **Audio Alerts**: Different sounds and volume levels for focus and rest periods
- **Obsidian Integration**: Optional quick access to Daily and Weekly notes in Obsidian and logging via the Local REST API ([see docs](docs/obsidian.md))
- **Window Management**:
  - Always-on-top functionality
  - Frameless window design
  - Drag to reposition (click and drag)
  - Resize capability (Ctrl + click and drag)
- **Customizable Settings**: Configuration saved in JSON format
- **Pause/Resume**: Ability to pause and resume timers as needed

## Requirements

- Python 3.13+
- PyQt6
- pygame

## Installation

### Option 1: Install from PyPI (Recommended)

Install the package directly using pip:

```bash
pip install pomodoro-timer
```

Run the application:

```bash
pomodoro
```

### Option 2: Install from Source

1. Clone this repository
2. Install the package in development mode:

```bash
pip install -e .
```

3. Run the application:

```bash
pomodoro
```

Or run directly:

```bash
python main.py
```

### Command Line Options

The application supports several command line options:

```bash
pomodoro --help                # Show help message
pomodoro --version             # Show version
pomodoro --focus 30            # 30 minute focus periods 
pomodoro --rest 10             # 10 minute rest periods
pomodoro --focus 45 --rest 15  # 45 minute focus, 15 minute rest
```

## Configuration

The application uses a `config.json` file to store user preferences:

- **Timer**: Configure focus and rest period durations
- **Sounds**: Set different sound files and volume levels for focus and rest periods
- **Obsidian**: Enable/disable integration, configure vault paths and REST API connection
- **UI**: Set window position, size, and appearance options

## Usage

1. Click the **Focus** button to start a Pomodoro session
   - You'll be prompted to enter what you're focusing on
2. Click the **Rest** button to start a break
3. Use the **Pause** button to pause/resume the current timer
4. Click the **Settings** button to customize your experience
5. If enabled, click **Daily** or **Weekly** to open corresponding notes in Obsidian
6. Click **Exit** to close the application

### Window Management

- Click and drag anywhere on the window to move it
- Hold Ctrl while clicking and dragging to resize the window

## Project Structure

The application is organized into modular components:

- `pomodoro/config.py`: Configuration management
- `pomodoro/sound.py`: Sound playback with volume control
- `pomodoro/notes.py`: Obsidian integration
- `pomodoro/session.py`: Session tracking and logging
- `pomodoro/ui_fixed.py`: User interface components

## Sound Files

Place your custom sound files in the `sounds/` directory:

- `focus_end.mp3`: Plays when a focus period ends (gentle sound recommended)
- `rest_end.mp3`: Plays when a rest period ends (louder sound recommended)

## Development History

The application has gone through multiple versions:

- `main_v1.py`: Initial implementation with basic Pomodoro functionality
- `main_v2.py`: Enhanced UI and Obsidian integration
- `main_new.py`: Current modular version with configuration support

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions, suggestions, and feedback are welcome! Feel free to submit a pull request or open an issue.
