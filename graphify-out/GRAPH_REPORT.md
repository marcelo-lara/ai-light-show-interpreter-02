# Graph Report - /home/darkangel/ai-light-show-interpreter-02  (2026-05-01)

## Corpus Check
- Corpus is ~17,612 words - fits in a single context window. You may not need a graph.

## Summary
- 235 nodes · 328 edges · 15 communities detected
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 71 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Musical State Timeline|Musical State Timeline]]
- [[_COMMUNITY_CLI Song Selection|CLI Song Selection]]
- [[_COMMUNITY_Data Contracts|Data Contracts]]
- [[_COMMUNITY_UI and DMX Flow|UI and DMX Flow]]
- [[_COMMUNITY_WebSocket Streaming Server|WebSocket Streaming Server]]
- [[_COMMUNITY_Evaluator and Shaders|Evaluator and Shaders]]
- [[_COMMUNITY_Evaluator Interface Contract|Evaluator Interface Contract]]
- [[_COMMUNITY_Deployment and UX Plan|Deployment and UX Plan]]
- [[_COMMUNITY_Compiler Test Coverage|Compiler Test Coverage]]
- [[_COMMUNITY_DMX File Writer|DMX File Writer]]
- [[_COMMUNITY_Stage Layout Export|Stage Layout Export]]
- [[_COMMUNITY_Engine Socket State|Engine Socket State]]
- [[_COMMUNITY_Shader Primitives|Shader Primitives]]
- [[_COMMUNITY_Waveform Playback Sync|Waveform Playback Sync]]
- [[_COMMUNITY_App Socket Integration|App Socket Integration]]

## God Nodes (most connected - your core abstractions)
1. `EngineWebSocketServer` - 23 edges
2. `build_musical_state_stream()` - 15 edges
3. `compile_dmx_show()` - 13 edges
4. `FakeScreen` - 11 edges
5. `Evaluator` - 10 edges
6. `DmxWriter` - 9 edges
7. `Audio to DMX Generation Specification` - 9 edges
8. `Compile DMX Show` - 8 edges
9. `main()` - 7 edges
10. `export_stage_layout_svg()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Show Name Validation` --implements--> `Audio to DMX Generation Specification`  [INFERRED]
  src/main.py → specs/001-fft-dmx-generator/spec.md
- `UI Playback Mode` --implements--> `Canvas Inspection UI Specification`  [AMBIGUOUS]
  src/main.py → specs/001-fft-dmx-generator/spec.md
- `Coordinate Warping` --implements--> `Audio to DMX Generation Specification`  [INFERRED]
  src/engine/evaluator.py → specs/001-fft-dmx-generator/spec.md
- `test_evaluator_produces_states_for_all_canvas_fixtures()` --calls--> `Evaluator`  [INFERRED]
  tests/integration/test_canvas_evaluation.py → src/engine/evaluator.py
- `NumPy Shader Evaluation Decision` --rationale_for--> `Runtime Evaluator`  [EXTRACTED]
  specs/001-fft-dmx-generator/research.md → src/engine/evaluator.py

## Hyperedges (group relationships)
- **Canvas Inspection WebSocket Contract** — websocket_emitter_init_payload, websocket_emitter_frame_payload, app_playback_inspection_app, enginecanvas_engine_canvas, mathparamspanel_math_params_panel [INFERRED 0.82]
- **DMX Compilation Pipeline** — show_compiler_compile_dmx_show, dmx_writer_dmx_writer, websocket_emitter_engine_websocket_server, test_output_contract_deterministic_dmx_output, test_output_contract_dmx_header_contract [EXTRACTED 0.93]
- **Shader Response Contract** — linear_wave_linear_wave, radial_pulse_radial_pulse, blending_additive_blend, blending_multiplicative_blend, test_shaders_shader_response_contract [EXTRACTED 0.95]
- **Waveform Media Sync** — waveformview_waveform_view, waveformview_audio_source, waveformview_playback_flag, waveformview_ready_gated_playback [EXTRACTED 0.93]
- **Engine Socket Runtime Contract** — useenginesocket_use_engine_socket, useenginesocket_engine_state, useenginesocket_websocket_session, useenginesocket_message_protocol, useenginesocket_reconnect_strategy, useenginesocket_fixture_state_merge, useenginesocket_play_command [EXTRACTED 0.94]

## Communities

### Community 0 - "Musical State Timeline"
Cohesion: 0.16
Nodes (25): dict, _anchor_matches(), ArtifactValidationError, build_musical_state_stream(), _build_section_progress(), _event_time(), _find_section(), _has_resolvable_anchor_reference() (+17 more)

### Community 1 - "CLI Song Selection"
Cohesion: 0.12
Nodes (14): artifact_dir_for_song(), artifact_missing(), list_song_choices(), main(), resolve_song_choice(), run_curses_selector(), validate_show_name(), FakeScreen (+6 more)

### Community 2 - "Data Contracts"
Cohesion: 0.1
Nodes (24): Data Folder Policy, DMX Show Frame, Event Cue Input, FFT Energy Input, Fixture Render State, Global Musical State Buffer, Virtual Canvas Schema, DMX Binary Format (+16 more)

### Community 3 - "UI and DMX Flow"
Cohesion: 0.11
Nodes (22): Playback Inspection App, DMX Writer, Moving-Head POI Pan/Tilt Mapping, Engine Canvas Component, Canvas Output HTML Shell, Derived Canvas POIs, Stage Layout SVG Export, React Bootstrap Entry (+14 more)

### Community 4 - "WebSocket Streaming Server"
Cohesion: 0.15
Nodes (2): create_websocket_server(), EngineWebSocketServer

### Community 5 - "Evaluator and Shaders"
Cohesion: 0.17
Nodes (9): Evaluator, additive_blend(), multiplicative_blend(), linear_wave(), radial_pulse(), _build_state(), test_blending_functions(), test_linear_wave_shape_and_response() (+1 more)

### Community 6 - "Evaluator Interface Contract"
Cohesion: 0.14
Nodes (12): EvaluatorInterface, FixtureRenderState, MusicalStateBuffer, procedural_shader_contract(), Contract Interface: Procedural Shader API This defines the structural boundaries, The `q_buffer` injected into all shaders per 20ms frame., Per-fixture render intent produced by the evaluator before DMX channel packing., Contract for rendering multiple shaders into a single output frame on a 2D mesh. (+4 more)

### Community 7 - "Deployment and UX Plan"
Cohesion: 0.18
Nodes (14): Canvas WebSocket Events, light-show-cli Docker Service, UI Docker Service, Canvas Mesh Renderer, CLI Entrypoint, Show Name Validation, Song Selection Flow, UI Playback Mode (+6 more)

### Community 8 - "Compiler Test Coverage"
Cohesion: 0.21
Nodes (9): test_compile_dmx_show_returns_expected_path(), test_evaluator_produces_states_for_all_canvas_fixtures(), test_invalid_show_name_is_rejected_by_main_invalid_path(), test_missing_artifact_directory_raises_error(), test_deterministic_dmx_byte_output(), test_dmx_header_structure_matches_spec(), test_render_duration_stays_within_sixty_seconds(), compile_dmx_show() (+1 more)

### Community 9 - "DMX File Writer"
Cohesion: 0.27
Nodes (2): _clamp_channel(), DmxWriter

### Community 10 - "Stage Layout Export"
Cohesion: 0.48
Nodes (5): _derive_canvas_pois(), _escape_xml(), export_stage_layout_svg(), _load_json(), test_export_stage_layout_svg_contains_fixture_and_poi_labels()

### Community 11 - "Engine Socket State"
Cohesion: 0.52
Nodes (7): Engine State Store, Fixture State Merge, Engine Message Protocol, Play Command Dispatch, Reconnect Strategy, useEngineSocket Hook, Canvas WebSocket Session

### Community 12 - "Shader Primitives"
Cohesion: 0.53
Nodes (6): Additive Blend, Multiplicative Blend, Linear Wave Shader, Radial Pulse Shader, Five-Band Musical State Contract Test, Shader Response Contract Test

### Community 13 - "Waveform Playback Sync"
Cohesion: 0.7
Nodes (5): Waveform Audio Source, External Playback Flag, Ready-Gated Playback Sync, WaveSurfer Lifecycle Management, WaveformView Component

### Community 14 - "App Socket Integration"
Cohesion: 0.5
Nodes (2): useEngineSocket(), App()

## Ambiguous Edges - Review These
- `Canvas Inspection UI Specification` → `UI Playback Mode`  [AMBIGUOUS]
  src/main.py · relation: implements

## Knowledge Gaps
- **28 isolated node(s):** `A dictionary-like container for per-frame musical render state.`, `Contract Interface: Procedural Shader API This defines the structural boundaries`, `The `q_buffer` injected into all shaders per 20ms frame.`, `Per-fixture render intent produced by the evaluator before DMX channel packing.`, `Contract for rendering multiple shaders into a single output frame on a 2D mesh.` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `WebSocket Streaming Server`** (21 nodes): `create_websocket_server()`, `EngineWebSocketServer`, `._add_client()`, `._broadcast()`, `._broadcast_ready_state()`, `._build_frame_payload()`, `._build_init_payload()`, `.cache_states()`, `.__init__()`, `.notify_ready()`, `._playback_loop()`, `._register_routes()`, `._remove_client()`, `._run()`, `._send_init()`, `._send_ready()`, `.set_evaluator()`, `.start()`, `._start_playback()`, `.wait_for_playback()`, `websocket_emitter.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `DMX File Writer`** (10 nodes): `_clamp_channel()`, `DmxWriter`, `.__enter__()`, `.__exit__()`, `.__init__()`, `._load_fixtures()`, `._load_pois()`, `.write_frame()`, `.write_header()`, `dmx_writer.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `App Socket Integration`** (4 nodes): `useEngineSocket()`, `App()`, `App.tsx`, `useEngineSocket.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Canvas Inspection UI Specification` and `UI Playback Mode`?**
  _Edge tagged AMBIGUOUS (relation: implements) - confidence is low._
- **Why does `compile_dmx_show()` connect `Compiler Test Coverage` to `Musical State Timeline`, `CLI Song Selection`, `Evaluator and Shaders`, `DMX File Writer`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `EngineWebSocketServer` connect `WebSocket Streaming Server` to `Musical State Timeline`, `CLI Song Selection`, `Evaluator and Shaders`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Why does `main()` connect `CLI Song Selection` to `Compiler Test Coverage`, `Stage Layout Export`, `WebSocket Streaming Server`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `EngineWebSocketServer` (e.g. with `Evaluator` and `MusicalStateBuffer`) actually correct?**
  _`EngineWebSocketServer` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `build_musical_state_stream()` (e.g. with `compile_dmx_show()` and `test_section_progress_and_label_propagation()`) actually correct?**
  _`build_musical_state_stream()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `compile_dmx_show()` (e.g. with `main()` and `ValueError`) actually correct?**
  _`compile_dmx_show()` has 11 INFERRED edges - model-reasoned connections that need verification._