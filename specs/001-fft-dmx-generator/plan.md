# Implementation Plan: Audio to DMX Generator

**Branch**: `001-fft-dmx-generator` | **Date**: 2026-04-27 | **Spec**: `specs/001-fft-dmx-generator/spec.md`
**Input**: Feature specification from `/specs/001-fft-dmx-generator/spec.md`

## Summary

Provide a terminal-first song selector that lets the user choose a track from `data/songs/*.mp3`, then render a binary DMX show file driven by a precomputed per-song 5-band FFT analysis. The pipeline uses a hybrid stage model: canonical rig and POI inputs come from `data/fixtures/*.json`, while app-specific virtual-canvas metadata lives in `src/config/stage_virtual_canvas.json`.

## Technical Context

**Language/Version**: Python 3.1x
**Primary Dependencies**: NumPy (rendering math), `curses` or `prompt_toolkit` (CLI UI)
**Storage**: Reading (read-only): `/data/songs/*.mp3`, `/data/artifacts/<Song - Artist>/essentia/fft_bands.json`, `/data/fixtures/*.json`, `src/config/stage_virtual_canvas.json`. Writing: `/data/shows/{song_name}.{show_name}.dmx`.
**Testing**: `pytest` (Default test fixture: `data/songs/Cinderella - Ella Lee.mp3`)
**Target Platform**: Linux (Docker containerized)
**Project Type**: CLI Application / Binary Generator Pipeline
**Performance Goals**: 50 FPS (20ms) rendering offline processing frame loop.
**Constraints**: MUST adhere to the read-only data policy outside `data/shows/`. MUST run securely in Docker. MUST compile exactly one `.dmx` binary file per run. Moving heads use configured POIs in v1 rather than dynamic brightest-region targeting.
**Scale/Scope**: Single stage visualization, handling arrays of 2D coordinates simultaneously.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Strict Read-Only Data Policy**: Verified. The system ONLY reads the JSON data and inputs for the `q_buffer`.
- **Single Output Target**: Verified. The output is exclusively `/data/shows/{song_name}.{show_name}.dmx`.
- **Core Pipeline (Rasterization)**: Verified. Evaluation relies strictly on the mathematical state of the canvas via coordinates and audio attack/release envelopes logic.
- **Docker-First Environment**: Verified. No external dependencies prevent containerization. All Python CLI UI scripts operate strictly inside the Linux terminal inside Docker.

## Project Structure

### Documentation (this feature)

```text
specs/001-fft-dmx-generator/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

```text
src/
├── main.py                     # Entrypoint (CLI UI for song selection)
├── config/
│   └── stage_virtual_canvas.json # App-specific render metadata for the virtual canvas
├── engine/
│   ├── evaluator.py            # Primary Loop / 2D Mesh construction + evaluation
│   ├── _q_buffer.py            # Musical State logic / smoothing
│   └── shaders/
│       ├── radial_pulse.py     # Drum hit shader
│       ├── linear_wave.py      # Ambient ambient shader
│       └── blending.py         # Multiplicative/Additive composer logic
└── io/
    ├── dmx_writer.py           # Struct packing for .dmx frames
    └── show_compiler.py        # Pipeline orchestrator

tests/
├── unit/
│   ├── test_q_buffer.py
│   └── test_shaders.py
└── integration/
    └── test_canvas_evaluation.py
```

**Structure Decision**: A single Python application divided into specific operational boundaries (`engine`, `io`, `config`). `src/` houses the system which processes song-scoped analysis artifacts, canonical fixture/POI inputs, and app-specific virtual-canvas metadata into a binary DMX show file.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
