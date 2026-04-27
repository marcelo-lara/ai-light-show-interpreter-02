# Tasks: Audio to DMX Generator

**Input**: Design documents from `/specs/001-fft-dmx-generator/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/evaluator.py

## User Story 1 - Song Selection via CLI

1. **[  ] [P] [US1] Create Docker Environment & Packaging**
   - **Goal**: Set up `Dockerfile` and `docker-compose.yml` to ensure Python execution within an isolated container.
   - **Instructions**: Create `docker-compose.yml` with a `light-show-cli` service pointing to `src/main.py`. Mount `data/` as a read-only volume and `data/shows/` as writable volume.
   - **Dependencies**: None
   - **Files to create/modify**: `Dockerfile`, `docker-compose.yml` 

2. **[  ] [P] [US1] Stage Virtual Canvas Config**
   - **Goal**: Create the app-specific virtual canvas metadata layered on top of the rig inputs.
   - **Instructions**: Create `src/config/stage_virtual_canvas.json` representing washers and moving heads on a 10x5m grid, derived from `data/fixtures/fixtures.json` and `data/fixtures/pois.json` according to the Data Model.
   - **Dependencies**: None
   - **Files to create/modify**: `src/config/stage_virtual_canvas.json`

3. **[  ] [ ] [US1] Curse-Based CLI Menu**
   - **Goal**: Create `src/main.py` entrypoint.
   - **Instructions**: Use Python `curses` to list files in `data/songs/*.mp3` matching requirement (no extension, `▶` indicator). Returns path to selected file.
   - **Dependencies**: Task 1
   - **Files to create/modify**: `src/main.py`

## User Story 2 - Audio Processing to DMX Generation

4. **[  ] [P] [US2] Musical State Buffer (Q-Buffer)**
   - **Goal**: Build data structure for smoothing audio into spatial properties.
   - **Instructions**: Create `src/engine/_q_buffer.py`. Implement class parsing `data/artifacts/<Song - Artist>/essentia/fft_bands.json` frame by frame, outputting a `MusicalStateBuffer` dict (`time`, `bands`, `intensity_hit`, `cumulative_rotation`, `mid_warp`).
   - **Dependencies**: None
   - **Files to create/modify**: `src/engine/_q_buffer.py`

5. **[  ] [ ] [US2] Evaluator Interface/Mesh**
   - **Goal**: Implement physical mappings and evaluate logic.
   - **Instructions**: Create `src/engine/evaluator.py`. Combine the derived `stage_virtual_canvas.json` metadata with rig and POI inputs, map the resulting fixture coordinates to NumPy (N, 2), and provide the `evaluate_frame` matrix math skeleton. 
   - **Dependencies**: Task 2, Task 4
   - **Files to create/modify**: `src/engine/evaluator.py`

6. **[  ] [P] [US2] Procedural Shaders**
   - **Goal**: Write functional logic for radial and linear pattern evaluations mapping to the (N,2) canvas points.
   - **Instructions**: Implement `src/engine/shaders/radial_pulse.py` and `src/engine/shaders/linear_wave.py` passing NumPy parameters. Implement Additive/Multiplicative Blending via `src/engine/shaders/blending.py`.
   - **Dependencies**: Task 5
   - **Files to create/modify**: `src/engine/shaders/radial_pulse.py`, `src/engine/shaders/linear_wave.py`, `src/engine/shaders/blending.py`

7. **[  ] [P] [US2] DMX Writer**
   - **Goal**: Pack mathematical intensities back into binary. 
   - **Instructions**: Create `src/io/dmx_writer.py`. Pack 512-byte universe structures using `struct` logic per frame and write output sequentially. 
   - **Dependencies**: Task 6
   - **Files to create/modify**: `src/io/dmx_writer.py`

8. **[  ] [ ] [US2] Show Compiler (Orchestrator)**
   - **Goal**: Stitch CLI parsing into the Engine, feeding it through the IO stream 50 times per second.
   - **Instructions**: Create `src/io/show_compiler.py`. Orchestrate `main.py` selection, frame iteration of `evaluator`, and dumping output via `dmx_writer.py`.  
   - **Dependencies**: Task 3, Task 5, Task 7
   - **Files to create/modify**: `src/io/show_compiler.py`, `src/main.py` (wiring)

## QA & Testing

9. **[  ] [ ] [QA] Integration Testing**
   - **Goal**: Create automated pipeline validation for the `Cinderella - Ella Lee` baseline fixture.
   - **Instructions**: Setup `tests/integration/test_canvas_evaluation.py`. End-to-end assert output `.dmx` binary properties are generated.
   - **Dependencies**: Task 8
   - **Files to create/modify**: `tests/integration/test_canvas_evaluation.py`