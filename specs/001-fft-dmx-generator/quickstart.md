# Quickstart: Canvas Output UI

## Overview
This feature introduces a live WebSocket-driven Web UI that renders a live 2D representation of the lighting engine's math variables and visual outputs concurrently. 

## 1. Prerequisites
1. **Docker Compose**: You must have `docker-compose` installed.
2. **Audio Track**: MP3 files required in `data/songs/` mapped to the corresponding analysis data in `data/artifacts/`.

## 2. Docker Deployment

Launch both the Python engine service and the Vite UI service.
```bash
docker compose up -d --build
```
> *Note:* The default `light-show-cli` service now starts in `--ui-playback` mode so the browser can drive song selection over the WebSocket service on port `3301`.

## 3. Accessing the Interface

1. Open your browser:
   ```text
   http://localhost:3300
   ```
2. Use the header dropdown to pick a song from `data/songs/`.
3. The frontend sends a `select_song` event over the WebSocket on port `3301`.
4. Wait for the backend to bake the `.dmx` file and emit `ready`.
5. Click **Play** to start synchronized audio playback and frame streaming.

*(The UI is exposed on port `3300` and the backend WebSocket runs on port `3301`.)

If you want to pre-bake a specific song without the browser workflow, you can still run:

```bash
docker compose run --rm light-show-cli --song "Cinderella - Ella Lee" --show-name main-show
```

## 4. UI Interactions
- **Header (Left)**: Choose a song from the mounted `/songs` list. While a new song is baking, the UI enters a loading state.
- **Waveform (Hero)**: Scrub through the audio and sync the timeline positioning using `waveform.js` (or modern equivalent `wavesurfer.js`).
- **Math View (Left Column)**: Lists realtime global musical state values (`q_buffer`).
- **Canvas Display (Right Column)**: 2D representation of the grid and generated fixture intensities.
