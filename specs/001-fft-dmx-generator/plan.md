# Implementation Plan: Canvas Output UI

**Branch**: `001-fft-dmx-generator` | **Date**: `2026-04-29` | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-fft-dmx-generator/spec.md` + Canvas User Request updates

## Summary

The user requested a simple React-based Web UI to view the complete Canvas applied with shaders, mathematical parameters of the shader engine, and the fixtures positioned on the virtual stage. This interface acts as an inspection tool (similar to BeatDrop-Music-Visualizer) to see the exact output of the shaders engine statically or over time, rather than a real-time standalone visualizer. This Canvas UI must be completely separated from the Python `/src` engine folder, residing in an isolated `/ui` Docker service, using a WebSocket stream to receive frame updates from the engine without writing intermediate artifacts to `/data`. The UI will leverage React with `wavesurfer.js` for audio playback and standard HTML5 `<canvas>` API for GPU-accelerated rendering.

## Technical Context

**Language/Version**: Python 3.11 (Backend Engine), TypeScript/React (Frontend UI)
**Primary Dependencies**: FastAPI / WebSockets (Python), Vite, React, wavesurfer.js (Frontend)
**Storage**: N/A (WebSocket streaming; final DMX targets `/data/shows/`)
**Testing**: `pytest` (Backend WS API), browser manual test (Frontend)
**Target Platform**: Docker-First environment (2 services: python-backend, node/nginx-ui)
**Project Type**: Mixed CLI/WebSocket Backend Engine + React Web Frontend  
**Performance Goals**: 50 FPS WebSocket data streaming to the browser over `localhost` mapped efficiently to a GPU-backed Canvas. 
**Constraints**: Absolute separation of `/ui` from `/src`, no modification to `/data` beyond DMX output (`Single Output Target`). Docker-first isolated environment.
**Scale/Scope**: Local developer visualizations; 1 UI container serving a Vite React app, 1 connected client.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
- **Strict Read-Only Data Policy**: PASS. No writes occur during WebSocket visualization.
- **Single Output Target**: PASS. Data is sent entirely over network stream; nothing touches the disk besides the eventual compiled DMX show. 
- **Core Pipeline (The Baker)**: PASS. Pipeline remains intact; WebSocket acts as a parallel observer subscribing to the evaluation stage.
- **Docker-First Environment**: PASS. Implementing as an independent `/ui` React app mapped to a docker service.

## Project Structure

### Documentation (this feature)

```text
specs/001-fft-dmx-generator/
├── plan.md              # This file
├── research.md          # Phase 0 output 
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output 
├── contracts/           # Phase 1 output 
│   ├── ui_websocket_contract.md
│   └── evaluator.py
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
docker-compose.yml       # Expanded to include `ui` service

src/                     # Unchanged except adding the WebSocket Server integration
├── main.py              
├── engine/              # Emits WebSockets events containing canvas meshes
│   ├── _q_buffer.py     # Transmits state parameter updates
│   ├── evaluator.py
│   └── shaders/
└── io/
    ├── dmx_writer.py
    └── websocket_emitter.py   # New file handling WS broadcast

ui/                      # New UI Service (Vite + React)
├── package.json
├── vite.config.ts
├── index.html           
├── src/
│   ├── App.tsx          # Main Layout (Waveform, Params, Canvas)
│   ├── components/      
│   │   ├── WaveformView.tsx
│   │   ├── MathParamsPanel.tsx
│   │   └── EngineCanvas.tsx # Handles HTML5 Canvas GPU rendering of the shader output
│   └── hooks/
│       └── useEngineSocket.ts
└── nginx.conf           # (Optional) specific overrides for Docker deploy
```

**Structure Decision**: A new top-level `ui/` directory containing a Vite React app, served by a Docker container. `src/io/websocket_emitter.py` handles the transmission of engine math/mesh state to connected UI clients.
