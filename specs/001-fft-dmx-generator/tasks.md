# Tasks: Audio to DMX Generator & Canvas Output UI

**Input**: Design documents from `/specs/001-fft-dmx-generator/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui_websocket_contract.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Since this specific plan incorporates the new user-requested Web UI, we have extended the tasks to include Phase 5 mapped to the Canvas User Story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for both backend and frontend.

- [x] T001 Create project structure for the `ui/` directory per the implementation plan.
- [x] T002 Initialize the React project with Vite (`npm create vite@latest ui -- --template react-ts`).
- [x] T003 Update `docker-compose.yml` to include the new `ui` service mapping to the Vite dev server.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

- [x] T004 Define `src/io/websocket_emitter.py` to handle the `asyncio` WebSocket server (`FastAPI` or `websockets`).
- [x] T005 [P] Create React `useEngineSocket.ts` hook in `ui/src/hooks/useEngineSocket.ts` to consume the WebSocket connection.
- [x] T006 [P] Add base canonical models for the 5-band evaluation and the DMX output in the Python engine.
- [x] T007 Initialize HTML5 Canvas API context helpers in `ui/src/components/EngineCanvas.tsx`.

---

## Phase 3: User Story 1 - Song Selection via CLI (Priority: P1) 🎯 MVP

**Goal**: As a user, I want to launch the application and see a list of my songs so that I can easily select which song to process for my light show.

**Independent Test**: Can be fully tested by launching the CLI, observing the list of mp3 files from `data/songs/`, navigating with arrow keys, and pressing enter to confirm a selection.

### Implementation for User Story 1

- [x] T008 [P] [US1] Implement the curses-based CLI song selector in `src/main.py` listing files from `data/songs/*.mp3`.
- [x] T009 [US1] Implement '▶' cursor and up/down arrow key navigation logic in `src/main.py`.
- [x] T010 [US1] Filter out `.mp3` extensions from menu display names.
- [x] T011 [US1] Accept an optional `--show-name` argument in the CLI entrypoint (`src/main.py`) defaulting to `main-show` with regex validation `^[A-Za-z0-9_-]+$`.

---

## Phase 4: User Story 2 - Audio Processing to DMX Generation (Priority: P1)

**Goal**: As a performer, I want the system to process the 5-band FFT and output a binary DMX file synchronized to the song's timbral complexity.

**Independent Test**: Select a valid song, evaluate the frame buffers, and confirm a binary DMX output file is created matching `data/shows/{song_name}.{show_name}.dmx`.

### Implementation for User Story 2

- [x] T012 [P] [US2] Implement `_q_buffer.py` to maintain global musical state, reading `fft_bands.json` and section metadata.
- [x] T013 [P] [US2] Implement `evaluator.py` using NumPy to map 5-band FFT energy onto the 2D stage canvas and fixtures.
- [x] T014 [US2] Implement procedural shaders (`RadialPulse`, `LinearWave`) in `src/engine/shaders/`.
- [x] T015 [US2] Implement layer blending and spatial coordinate distortion based on `q_buffer` state.
- [x] T016 [US2] Implement binary DMX frame construction in `src/io/dmx_writer.py` mapping evaluated values to 512-byte universes.
- [x] T017 [US2] Ensure fallback logic to transient detection from the 5-band analysis when optional `lighting_events.json` is missing or invalid.
- [x] T018 [US2] Save output file cleanly to `data/shows/{song_name}.{show_name}.dmx`, handling safe interruption (Ctrl+C).

---

## Phase 5: User Story 3 - Canvas Output Inspection UI (Priority: P2)

**Goal**: I want an inspection UI (like BeatDrop-Music-Visualizer) to see the exact 2D math output of the shaders engine over a WebSocket, decoupled from the DMX writer.

**Independent Test**: Open `http://localhost:3300`, select a song in the UI dropdown, and observe the waveform, math parameters, and updating HTML5 canvas.

### Implementation for User Story 3

- [x] T019 [P] [US3] Scaffold the Vite-backed UI container and update `docker-compose.yml` to expose port 3300 for the frontend and 3301 for the Python Engine WebSocket, mounting `/data/songs/` into the UI service for audio streaming.
- [x] T020 [US3] Update `src/main.py` main loop to keep the backend alive in UI playback mode, accept song selection from the browser, bake the entire `.dmx` at maximum speed, then emit `ready` locally via `websocket_emitter.py`.
- [x] T021 [US3] Implement logic in `websocket_emitter.py` to listen for `select_song` and `play` intents from the frontend, rebake and republish state on song changes, then stream cached `init` and `frame` payloads at 1x real-time speed (50 FPS).
- [x] T022 [P] [US3] Scaffold the React main layout in `ui/src/App.tsx`.
- [x] T023 [P] [US3] Implement `ui/src/components/WaveformView.tsx` utilizing `wavesurfer.js` to render the song timeline via static file fetch, enabling the play button only when `ready` is received.
- [x] T024 [P] [US3] Implement `ui/src/components/MathParamsPanel.tsx` to reactively display `q_buffer` parameters from WebSocket state.
- [x] T025 [P] [US3] Implement `ui/src/components/EngineCanvas.tsx`, using standard HTML5 Canvas 2D context to render the `canvas_mesh.pixels` block rapidly via the browser render loop.
- [x] T026 [US3] Render discrete fixture indicators as simple colored geometry on top of `EngineCanvas.tsx` while tracking real-time coordinated intensity.
- [x] T027 [US3] Handle the `end` event cleanly in the React frontend, resetting or stopping the playback loop.


---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [x] T028 [P] Documentation updates in `README.md`, `docs/README.md`, and feature quickstart docs reflecting the UI service ports and WebSocket dependencies.
- [x] T029 Clean up unused imports and standardize logging across `src/io/`.
- [x] T030 Ensure the `data/` read-only constitution is completely preserved (engine emits to UI exclusively via network).
- [x] T031 Run standard test suite to ensure the WebSocket addition does not bottleneck the existing DMX generation thread.

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational phase completion.
  - Phase 3 (CLI) and Phase 4 (Engine) can be done in parallel.
  - Phase 5 (UI) requires Phase 4 Engine math/evaluator work as a precursor or concurrent dependency.

### Parallel Opportunities
- React Component scaffolding (T022-T025) can be done concurrently with the Python `evaluator.py` (T013) implementation.
- WebSocket Emitter (T004) and Consumer Hook (T005) are entirely decoupled and parallelizable.
