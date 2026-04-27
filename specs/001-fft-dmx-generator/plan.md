# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.1x
**Primary Dependencies**: NumPy (rendering math), `curses` or `prompt_toolkit` (CLI UI)
**Storage**: Reading (read-only): `/data/songs/*.mp3`, `/data/essentia/fft_bands.json`, `.json` configuration. Writing: `/data/shows/*.dmx` (binary).
**Testing**: `pytest` (Default test fixture: `data/songs/Cinderella - Ella Lee.mp3`)
**Target Platform**: Linux (Docker containerized)
**Project Type**: CLI Application / Binary Generator Pipeline
**Performance Goals**: 50 FPS (20ms) rendering offline processing frame loop.
**Constraints**: MUST adhere to Read-Only policy for input data. MUST run securely in Docker. MUST compile exactly one `.dmx` binary file out.
**Scale/Scope**: Single stage visualization, handling arrays of 2D coordinates simultaneously.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Strict Read-Only Data Policy**: Verified. The system ONLY reads the JSON data and inputs for the `q_buffer`.
- **Single Output Target**: Verified. The output is exclusively `/data/shows/<song>.dmx`.
- **Core Pipeline (Rasterization)**: Verified. Evaluation relies strictly on the mathematical state of the canvas via coordinates and audio attack/release envelopes logic.
- **Docker-First Environment**: Verified. No external dependencies prevent containerization. All Python CLI UI scripts operate strictly inside the Linux terminal inside Docker.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
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
│   └── stage_virtual_canvas.json # Fixture manifest and canvas boundaries
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

**Structure Decision**: A single Python application divided into specific operational boundaries (`engine`, `io`, `config`). `src/` houses the system which processes the JSON artifact data to binary DMX.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
