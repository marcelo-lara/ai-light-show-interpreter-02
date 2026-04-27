# Quickstart: Audio to DMX Generator

## Prerequisites
- Docker & Docker Compose
- Ensure input directory `data/songs/` has `.mp3` files.
- Ensure per-song 5-band analysis artifacts are already generated at `data/artifacts/<Song - Artist>/essentia/fft_bands.json`.
- Ensure rig inputs exist at `data/fixtures/fixtures.json` and `data/fixtures/pois.json`.

## Execution

1. Build the Docker environment:
   ```bash
   docker compose build
   ```
2. Start the interactive CLI:
   ```bash
   docker compose run --rm light-show-cli
   ```
3. Use Arrow Keys to navigate the playlist of `.mp3` tracks (Select `Cinderella - Ella Lee` for baseline testing).
4. Press `Enter` to select a track.
5. The `Evaluator` will combine fixture and POI inputs with `stage_virtual_canvas.json` metadata, process the 5-band FFT `q_buffer`, inject it into the `Radial Pulse` and `Linear Wave` shaders, and bake a binary 50FPS `.dmx` sequence into `data/shows/{song_name}.{show_name}.dmx`.

## Verification

Check the output directory for your compiled show:
```bash
ls -la data/shows/*.dmx
```
