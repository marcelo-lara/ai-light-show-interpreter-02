# Quickstart: Canvas Output UI

## Overview
This feature introduces a live WebSocket-driven Web UI that renders a live 2D representation of the lighting engine's math variables and visual outputs concurrently. 

## 1. Prerequisites
1. **Docker Compose**: You must have `docker-compose` installed.
2. **Audio Track**: MP3 files required in `data/songs/` mapped to the corresponding analysis data in `data/artifacts/`.

## 2. Docker Deployment

Launch both the python engine service and the static UI server.
```bash
docker compose up -d --build
```
> *Note:* The `docker-compose.yml` has been updated to include the `ui` service.

## 3. Accessing the Interface

1. Start processing your show using the CLI in the Python container.
   ```bash
   docker compose run --service-ports --rm light-show-cli --song "Cinderella - Ella Lee" --ui-playback
   ```
2. Once the song begins rendering (or after you've selected a song via CLI), open your browser:
   ```text
   http://localhost:3300
   ```
*(The UI is exposed on port `3300` and the backend WebSocket runs on port `3301`.)

## 4. UI Interactions
- **Header (Left)**: View the current song name originating from `/data/songs`.
- **Waveform (Hero)**: Scrub through the audio and sync the timeline positioning using `waveform.js` (or modern equivalent `wavesurfer.js`).
- **Math View (Left Column)**: Lists realtime global musical state values (`q_buffer`).
- **Canvas Display (Right Column)**: 2D representation of the grid and generated fixture intensities.
