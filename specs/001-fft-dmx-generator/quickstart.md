# Quickstart: Audio to DMX Generator

## Prerequisites
- Docker & Docker Compose
- Run the CLI from an interactive terminal because the selector uses `curses`.
- Ensure input directory `data/songs/` has `.mp3` files.
- Ensure per-song beat and duration metadata is already generated at `data/artifacts/<Song - Artist>/essentia/beats.json`.
- Ensure per-song section metadata is already generated at `data/artifacts/<Song - Artist>/section_segmentation/sections.json`.
- Ensure per-song 5-band analysis artifacts are already generated at `data/artifacts/<Song - Artist>/essentia/fft_bands.json`.
- Ensure rig inputs exist at `data/fixtures/fixtures.json` and `data/fixtures/pois.json`.

## Execution

1. Build the Docker environment:
   ```bash
   docker compose build
   ```
2. Start the interactive CLI:
   ```bash
   docker compose run --rm light-show-cli --show-name main-show
   ```
3. Use Arrow Keys to navigate the playlist of `.mp3` tracks (Select `Cinderella - Ella Lee` for baseline testing).
4. Press `Enter` to select a track.
5. The `Evaluator` will combine fixture and POI inputs with `stage_virtual_canvas.json` metadata, process section metadata and the 5-band FFT `q_buffer`, optionally ingest `lighting_events.json`, emit per-fixture render states, and the DMX writer will bake those states into a binary 50FPS `.dmx` sequence at `data/shows/{song_name}.{show_name}.dmx`.

## Verification

Check the output directory for your compiled show:
```bash
ls -la data/shows/*.dmx
```
