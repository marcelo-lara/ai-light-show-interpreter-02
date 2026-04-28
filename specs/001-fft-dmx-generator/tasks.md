# Tasks: Audio to DMX Generator

**Input**: Design documents from `/specs/001-fft-dmx-generator/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/evaluator.py

## User Story 1 - Song Selection via CLI

1. **[X] [P] [US1] Create Docker Environment & Packaging**
   - **Goal**: Set up `Dockerfile` and `docker-compose.yml` to ensure Python execution within an isolated container.
   - **Instructions**: Create `Dockerfile`, `docker-compose.yml`, and `requirements.txt` for a `light-show-cli` service that installs runtime/test dependencies, points to `src/main.py`, enables interactive TTY/stdin for the `curses` selector, mounts `data/` as a read-only volume, and mounts `data/shows/` as writable.
   - **Dependencies**: None
   - **Files to create/modify**: `Dockerfile`, `docker-compose.yml`, `requirements.txt` 

2. **[X] [P] [US1] Stage Virtual Canvas Config**
   - **Goal**: Create the app-specific virtual canvas metadata layered on top of the rig inputs.
   - **Instructions**: Create `src/config/stage_virtual_canvas.json` representing washers and moving heads on a 10x5m grid, derived from canonical fixture geometry in `data/fixtures/fixtures.json` and target POIs in `data/fixtures/pois.json` according to the Data Model. Map normalized canonical fixture coordinates onto the 10x5 canvas by linear scaling.
   - **Dependencies**: None
   - **Files to create/modify**: `src/config/stage_virtual_canvas.json`

3. **[X] [ ] [US1] Curse-Based CLI Menu**
   - **Goal**: Create `src/main.py` entrypoint.
   - **Instructions**: Use Python `curses` to list files in `data/songs/*.mp3` matching requirement (no extension, `▶` indicator), accept an optional `--show-name` argument, reject values that do not match `^[A-Za-z0-9_-]+$`, and return the selected song path plus the resolved output show name.
   - **Dependencies**: Task 1
   - **Files to create/modify**: `src/main.py`

4. **[X] [ ] [US1] CLI Empty-State and Interrupt Handling**
   - **Goal**: Cover the non-happy-path entrypoint behaviors required by the spec.
   - **Instructions**: Update the CLI flow to show a clear message and exit non-zero when `data/songs/` is empty or missing, and to exit cleanly when the user interrupts before rendering begins.
   - **Dependencies**: Task 3
   - **Files to create/modify**: `src/main.py`

## User Story 2 - Audio Processing to DMX Generation

5. **[X] [P] [US2] Section and Musical State Inputs**
   - **Goal**: Build the input layer for smoothing audio and section-aware rendering.
   - **Instructions**: Create `src/engine/_q_buffer.py`. Implement code that parses `data/artifacts/<Song - Artist>/essentia/beats.json`, `data/artifacts/<Song - Artist>/section_segmentation/sections.json`, and `data/artifacts/<Song - Artist>/essentia/fft_bands.json` frame by frame, applies configurable attack/release smoothing, and outputs section-aware musical state data including `MusicalStateBuffer` (`time`, `bands`, `intensity_hit`, `cumulative_rotation`, `mid_warp`, `section_label`, `section_progress`, `cue_trigger`).
   - **Dependencies**: None
   - **Files to create/modify**: `src/engine/_q_buffer.py`

6. **[X] [ ] [US2] Event Cue Fallback Contract**
   - **Goal**: Define how optional event cue input affects rendering without becoming a required dependency.
   - **Instructions**: Implement event cue ingestion so `lighting_events.json` is consumed only when it parses successfully, all cue records are minimally valid, and cue timestamps are monotonically increasing within the selected song duration; otherwise ignore the event file for that song and populate `cue_trigger` via transient detection from FFT energy.
   - **Dependencies**: Task 5
   - **Files to create/modify**: `src/engine/_q_buffer.py`

7. **[X] [ ] [US2] Evaluator Interface/Mesh**
   - **Goal**: Implement physical mappings and evaluate logic.
   - **Instructions**: Create `src/engine/evaluator.py`. Combine the derived `stage_virtual_canvas.json` metadata with rig and POI inputs, map the resulting fixture coordinates to NumPy (N, 2), apply section-aware routing and spatial warping hooks, and assemble one per-fixture render state from the shader outputs using canonical fixture ids from `source_fixture_id`.
   - **Dependencies**: Task 2, Task 5, Task 6, Task 8
   - **Files to create/modify**: `src/engine/evaluator.py`

8. **[X] [P] [US2] Procedural Shaders**
   - **Goal**: Write functional logic for radial and linear pattern evaluations mapping to the (N,2) canvas points.
   - **Instructions**: Implement `src/engine/shaders/radial_pulse.py` and `src/engine/shaders/linear_wave.py` passing NumPy parameters. Implement Additive/Multiplicative Blending via `src/engine/shaders/blending.py`, including low-intensity behavior during quiet or silent passages, so Task 7 can assemble final render states from these shader outputs.
   - **Dependencies**: Task 5
   - **Files to create/modify**: `src/engine/shaders/radial_pulse.py`, `src/engine/shaders/linear_wave.py`, `src/engine/shaders/blending.py`

9. **[X] [P] [US2] DMX Writer**
   - **Goal**: Pack mathematical intensities back into binary. 
   - **Instructions**: Create `src/io/dmx_writer.py`. Map evaluator render states onto actual fixture channels using canonical fixture/template metadata, pack the DMX header and timestamped frame records with `struct`, and ensure interrupted or failed renders do not leave partial output files behind.
   - **Dependencies**: Task 7, Task 8
   - **Files to create/modify**: `src/io/dmx_writer.py`

10. **[X] [ ] [US2] Show Compiler (Orchestrator)**
   - **Goal**: Stitch CLI parsing into the Engine, feeding it through the IO stream 50 times per second.
   - **Instructions**: Create `src/io/show_compiler.py`. Orchestrate `main.py` selection, artifact validation including exact MP3-basename to artifact-directory matching, required beat/section/FFT input loading, optional event cue loading, frame iteration of `evaluator`, dumping output via `dmx_writer.py` using the default show name `main-show` unless an explicit show name is provided, and clean interruption handling during rendering.
   - **Dependencies**: Task 4, Task 7, Task 9
   - **Files to create/modify**: `src/io/show_compiler.py`, `src/main.py` (wiring)

## QA & Testing

11. **[X] [P] [QA] Unit Tests for Q-Buffer and Shaders**
   - **Goal**: Validate the core musical-state and shader behaviors in isolation.
   - **Instructions**: Add `tests/unit/test_q_buffer.py` and `tests/unit/test_shaders.py` covering configurable attack/release smoothing, section-label propagation, observable section-driven render differences, rejection of FFT frames that do not contain exactly 5 values, cue validation against duration from `beats.json`, valid `lighting_events.json` cue ingestion, rejection of out-of-order cue timestamps, full fallback when any cue record is malformed, transient fallback behavior, spatial warping inputs, and low-intensity output during silence. Run these checks in Docker.
   - **Dependencies**: Task 5, Task 6, Task 8
   - **Files to create/modify**: `tests/unit/test_q_buffer.py`, `tests/unit/test_shaders.py`

12. **[X] [P] [QA] CLI and Error-Handling Tests**
   - **Goal**: Validate non-happy-path entrypoint behavior.
   - **Instructions**: Add `tests/unit/test_cli_menu.py` and `tests/integration/test_error_handling.py` covering `.mp3` extension stripping, rendering and movement of the literal `▶` selector indicator, arrow-key navigation with Enter selection, listing songs even when their render artifacts are missing, empty or missing song directories, exact artifact-directory matching from the selected MP3 basename, missing or malformed beat/duration metadata, invalid analysis inputs, invalid `--show-name` rejection against `^[A-Za-z0-9_-]+$`, and clean interruption semantics. Run these checks in Docker.
   - **Dependencies**: Task 4, Task 10
   - **Files to create/modify**: `tests/unit/test_cli_menu.py`, `tests/integration/test_error_handling.py`

13. **[X] [ ] [QA] Integration and Output Contract Testing**
   - **Goal**: Create automated pipeline validation for the baseline song and DMX output contract.
   - **Instructions**: Add `tests/integration/test_canvas_evaluation.py` and `tests/integration/test_output_contract.py` to assert output generation, exact `{song_name}.{show_name}.dmx` filename behavior with both the `main-show` default and a user-supplied `--show-name`, DMX header and frame-record structure, deterministic identical output bytes across repeated runs with the same inputs, render states keyed by canonical fixture ids, DMX-bound numeric channel intent values, distinct washer versus moving-head behavior including direct POI pan/tilt lookup from `pois.json`, CLI startup from process launch to first rendered menu within 1 second, and baseline render duration from song confirmation to completed DMX write within 60 seconds. Run these checks in Docker.
   - **Dependencies**: Task 10
   - **Files to create/modify**: `tests/integration/test_canvas_evaluation.py`, `tests/integration/test_output_contract.py`

14. **[X] [ ] [QA] Docker Smoke Test**
   - **Goal**: Validate the completed feature in the required Docker-first environment.
   - **Instructions**: Rebuild the Docker image, run the CLI end to end inside Docker, and verify the baseline song render succeeds without violating the read-only data rules.
   - **Dependencies**: Task 13
   - **Files to create/modify**: `Dockerfile`, `docker-compose.yml`