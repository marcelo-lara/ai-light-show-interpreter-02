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

* **Decision**: `curses`
* **Rationale**: `curses` is built into the Python standard library, requiring no extra dependencies. Given the Docker constraint and Linux-only target, standard `curses` is reliable for a simple list selector while keeping the dependency surface narrow.
* **Alternatives considered**: `questionary`, `rich`. (These are great but might be overkill for a single list selection).

## 3. Fixture/Canvas Data Structure
**Task**: Find patterns for storing DMX fixture configuration on a 2D Stage Virtual Canvas.
**Context**: We need a schema (`stage_virtual_canvas.json`) that treats fixtures as lights in a 2D space. Parcans are static washers, moving heads can point anywhere.
* **Decision**: Use a hybrid model where `data/fixtures/fixtures.json` and `data/fixtures/pois.json` remain canonical for fixture identity, channel ownership, and target points, while `stage_virtual_canvas.json` stores only app-specific sampling/grouping metadata and coordinate derivations.
* **Rationale**: This avoids duplicating DMX ownership in two places while still providing a compact render-oriented canvas description that feeds directly into a NumPy coordinate array at startup.

## 4. Evaluator-to-DMX Contract
**Task**: Define the handoff boundary between mathematical rendering and DMX channel packing.
**Context**: The evaluator samples shader output on the virtual canvas, but the DMX writer must still map those results onto fixture-specific channel layouts for washers and moving heads.
* **Decision**: The evaluator returns per-fixture render intents containing `fixture_id`, `dimmer`, `color_rgb`, and optional `target_poi`; the DMX writer converts that render state into actual DMX channels using canonical fixture metadata.
* **Rationale**: This keeps mathematical rendering separate from fixture-template addressing, which is the cleanest boundary for testing and minimizes duplicated DMX logic.

## 5. DMX Binary Format Construction
**Task**: Find best practices for writing binary sequence files in Python.
**Context**: The final output is a `.dmx` file containing sequential frames of 512-byte (universe) values.
* **Decision**: Use Python's `struct` module or raw `bytes()` / `bytearray()`.
* **Rationale**: A DMX universe frame is just an array of 512 bytes (values 0-255). Writing a pure continuous byte stream matching 50 frames per second is highly efficient.

