# Research: Audio to DMX Generator

## 1. Matrix Math vs. Pure Python for Shader Engine
**Task**: Compare rendering libraries (e.g., NumPy for matrix math vs. pure Python).
**Context**: We need to perform 2D spatial Math across a stage canvas at 50 FPS (20ms frames), warping coordinates and blending multiple procedural shaders (Radial Pulse, Linear Wave), based on audio-reactive data (`q_buffer`).

* **Decision**: NumPy
* **Rationale**: NumPy processes large arrays of 2D coordinates simultaneously (vectorization) which is orders of magnitude faster than iterating through them with pure Python `for` loops in every 20ms frame. With layer blending and multiple active shaders (e.g., coordinate warping based on mid-range FFT energy), NumPy will easily maintain the 50 FPS performance goal, whereas pure Python might struggle.
* **Alternatives considered**: Pure Python math module (too slow for per-fixture, per-frame evaluation of complex procedural math).

## 2. Terminal UI (TUI) Library for CLI
**Task**: Find best practices for building an interactive file selector in a Python CLI.
**Context**: The application entry point requires listing songs (`data/songs/*.mp3`), showing a `▶` indicator on the left, and navigating with Up/Down keys, selecting with Enter.

* **Decision**: `curses` (built-in) or `prompt_toolkit`
* **Rationale**: `curses` is built into the Python standard library, requiring no extra dependencies. However, for modern Python CLIs, a lightweight dependency like `inquirer` or `prompt_toolkit` provides a cleaner, more robust cross-platform API for a simple list selection. Given the Docker constraint, standard `curses` is extremely reliable on Linux. We'll use `curses` to keep dependencies strictly analytical (NumPy).
* **Alternatives considered**: `questionary`, `rich`. (These are great but might be overkill for a single list selection).

## 3. Fixture/Canvas Data Structure
**Task**: Find patterns for storing DMX fixture configuration on a 2D Stage Virtual Canvas.
**Context**: We need a schema (`stage_virtual_canvas.json`) that treats fixtures as lights in a 2D space. Parcans are static washers, moving heads can point anywhere.
* **Decision**: A JSON manifest storing an array of fixture objects containing: `id`, `type` (washer/moving_head), `dmx_start_channel`, `channel_count`, and `canvas_position` (x, y coordinates).
* **Rationale**: Simple serialization that feeds directly into a NumPy coordinate array at startup.

## 4. DMX Binary Format Construction
**Task**: Find best practices for writing binary sequence files in Python.
**Context**: The final output is a `.dmx` file containing sequential frames of 512-byte (universe) values.
* **Decision**: Use Python's `struct` module or raw `bytes()` / `bytearray()`.
* **Rationale**: A DMX universe frame is just an array of 512 bytes (values 0-255). Writing a pure continuous byte stream matching 50 frames per second is highly efficient.

