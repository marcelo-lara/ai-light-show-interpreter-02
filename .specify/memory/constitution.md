<!--
Sync Impact Report:
- Version change: Initial Draft -> 1.0.0
- List of modified principles:
  - Added "Strict Read-Only Data Policy"
  - Added "Single Output Target"
  - Added "Core Pipeline"
  - Added "Docker-First Environment"
  - Added "Defined Inputs and Fallbacks"
- Added sections: Core Principles, Governance
- Removed sections: N/A (Initial Template)
- Templates requiring updates: 
  - ⚠ `.specify/templates/plan-template.md`
  - ⚠ `.specify/templates/spec-template.md`
  - ⚠ `.specify/templates/tasks-template.md`
- Follow-up TODOs: None.
-->

# ai-light-show-interpreter-02 Constitution

## Core Principles

### I. Strict Read-Only Data Policy
The `/data` folder is strictly read-only. We must never mutate source audio, artifacts, or intelligence outputs. This ensures data integrity from the upstream song analyzer and prevents accidental corruption of the semantic intelligence artifacts.

### II. Single Output Target
The ONLY write operation allowed by this repository is compiling `.dmx` binary show files (e.g., `[Song].show_[Date].dmx`) inside the `/data/shows/` directory. All other files and directories within the `/data` folder are strictly off-limits for write operations. No other artifacts or intermediate data are generated.

### III. Core Pipeline (The Baker)
The rendering pipeline operates strictly as a rasterizer and baker. It must follow this exact sequence:
1. **Coordinate Lookup**: Retrieve $(x, y)$ positions for each fixture defined in the Stage Virtual Canvas.
2. **Smoothing & Evaluation**: Apply configurable exponential smoothing (attack/release envelopes) to raw audio (FFT bands) for every 20ms frame (at 50 FPS), then evaluate the mathematical state of the canvas.
3. **Rasterization**: Sample color and brightness at each fixture's coordinate on the 2D grid.
4. **Baking**: Write the sampled results directly into the binary DMX frame.

### IV. Docker-First Environment
All implementations, tasks, and scripts must be run inside Docker containers. Local virtual environments are strictly prohibited. Temporary patching code, one-off scripts, or scaffolding files must always be cleaned up after use. A full smoke test must be performed by rebuilding the Docker container (e.g., `docker compose build` or `docker compose up -d --build`) at the end of feature implementation to verify correctness.

### V. Defined Inputs and Fallbacks
The interpreter consumes specific semantic artifacts:
* `sections.json`: Determines section-based rendering structure/logic.
* `essentia/fft_bands.json`: Provides raw, frame-by-frame frequency energy levels.
* `song_event_timeline.json`: (Optional) Triggers instantaneous mathematical "Hard Cuts" or coordinate shifts. If missing or untrusted, the system MUST fallback to dynamically detecting transients (sudden energy spikes) directly from the `essentia/fft_bands.json` stream.

### VI. Code Organization and Structure
Do not create large files. As a guideline, files should generally not exceed 200 lines (though this is not a strict limit). Instead of large monolithic files, create well-organized folders with intended purposes and modularized code. ALWAYS follow best practices for Python development.

## Governance

All scripts, agents, and contributors must verify compliance with these core principles. The read-only data policy and Docker environment constraints are absolute. 

- **Amendment Procedure**: Any changes to these core principles or architecture must be updated in this constitution and submitted as a dedicated pull request.
- **Versioning Policy**: Major version increments for architectural changes, Minor for added principles, Patch for clarifications.
- **Compliance Review**: Agents executing plans or creating specifications must explicitly verify alignment with the "Single Output Target" and "Docker-First" rules before proposing changes.

**Version**: 1.0.0 | **Ratified**: 2026-04-27 | **Last Amended**: 2026-04-27
