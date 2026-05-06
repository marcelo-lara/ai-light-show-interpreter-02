<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
[specs/001-fft-dmx-generator/plan.md](specs/001-fft-dmx-generator/plan.md)
<!-- SPECKIT END -->

## Project Instructions

- The repository is currently in SpecKit SDD mode. When spec, plan, task, and doc artifacts disagree, resolve the inconsistency explicitly instead of guessing an implementation contract.
- Treat all paths under `data/` as read-only except for `data/shows/`, which is the only valid output directory.
- The canonical per-song 5-band FFT input is `data/artifacts/<Song - Artist>/essentia/fft_bands.json`.
- Use a hybrid fixture ownership model: `data/fixtures/fixtures.json` and `data/fixtures/pois.json` are the canonical rig and targeting inputs; `src/config/stage_virtual_canvas.json` is limited to app-specific render metadata derived around those inputs.
- For v1 behavior, moving heads target named POIs from `data/fixtures/pois.json`; do not design v1 around dynamic brightest-region search across the canvas.
- The canonical DMX output naming convention is `data/shows/{song_name}.{show_name}.dmx`.
- During spec work, keep implementation-detail decisions in planning artifacts and keep the feature spec focused on user-visible behavior, acceptance criteria, and edge-case handling.

## graphify

Before answering architecture or codebase questions, read `graphify-out/GRAPH_REPORT.md` if it exists.
If `graphify-out/wiki/index.md` exists, navigate it for deep questions.
Type `/graphify` in Copilot Chat to build or update the knowledge graph.
