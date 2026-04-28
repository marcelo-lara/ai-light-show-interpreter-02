# Feature Specification: Audio to DMX Generator with CLI

**Feature Branch**: `001-fft-dmx-generator`  
**Created**: 2026-04-27
**Status**: Implemented and Validated  
**Input**: User description: "CLI-UI the entrypoint of this python application should be a list of the songs from data/songs/*.mp3 without the file extension. an '▶' should be on the left of each song item, and use the cursor keys to move between songs, and 'enter' to select a song. As a performer, I want my lights to react to 5-band FFT energy so that the visual intensity matches the timbral complexity of my music. at the end, I need to have a binary DMX file to perform the show."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Song Selection via CLI (Priority: P1)

As a user, I want to launch the application and see a list of my songs so that I can easily select which song to process for my light show.

**Why this priority**: It is the primary entrypoint for the application and is required before any processing can occur.

**Independent Test**: Can be fully tested by launching the CLI, observing the list of mp3 files from `data/songs/`, navigating with arrow keys, and pressing enter to confirm a selection.

**Acceptance Scenarios**:

1. **Given** the `data/songs/` directory contains mp3 files, **When** I run the entrypoint, **Then** I see the list of song names without the `.mp3` extension.
2. **Given** a song exists in `data/songs/` but its required render artifacts are missing, **When** the entrypoint lists songs, **Then** that song still appears in the list and the system reports the artifact problem only when the user selects it.
3. **Given** the song list is displayed, **When** I use the up/down cursor keys, **Then** an '▶' indicator moves to the currently highlighted song.
4. **Given** a song is highlighted with the '▶' indicator, **When** I press 'Enter', **Then** the application selects this song for processing.

---

### User Story 2 - Audio Processing to DMX Generation (Priority: P1)

As a performer, I want the system to use the selected song's precomputed 5-band FFT analysis and output a binary DMX file so that my lights react proportionally to the song's timbral complexity during my show.

**Why this priority**: This provides the core value of translating the music into the required physical output format (DMX) for performance.

**Independent Test**: Can be fully tested by selecting a song with matching precomputed artifacts, processing those artifacts, and validating that a binary DMX output file is created and contains control data synchronized to the song.

**Acceptance Scenarios**:

1. **Given** a song has been selected and its FFT analysis is available, **When** the application processes it, **Then** it resolves that input into exactly 5 canonical energy bands to drive the light show.
2. **Given** the 5-band energy is available, **When** generating the light show, **Then** the visual intensity changes in proportion to those energy levels.
3. **Given** section metadata exists for the selected song, **When** the application generates the show, **Then** it can vary rendering behavior across the song structure.
4. **Given** validated event cue data is available from the optional event layer, **When** the application generates the show, **Then** it may use that cue data to trigger discrete visual accents.
5. **Given** event cue data is unavailable or invalid, **When** the application generates the show, **Then** it falls back to transient detection from the 5-band analysis without failing the render.
6. **Given** the processing is complete, **When** the application finishes, **Then** a binary DMX show file is produced for use in the performance using a deterministic show name.
7. **Given** the user does not provide a show name, **When** the application writes the output, **Then** it uses `main-show` as the show name segment of the filename.
8. **Given** the user provides a show name, **When** the application writes the output, **Then** it uses that show name in the `{song_name}.{show_name}.dmx` filename.

### Edge Cases

- If the song directory is empty or missing, the system shows a clear message and exits without starting processing.
- If the selected song or its required analysis inputs are unreadable or invalid, the system aborts with a clear error and does not write a partial show file.
- If any FFT frame cannot be resolved into exactly 5 canonical energy values from a supported upstream layout, the system aborts with a clear error and does not attempt rendering.
- If required beat and duration metadata is missing or malformed, the system aborts with a clear error and does not attempt cue validation or output generation.
- If optional event cue data is missing or invalid, the system continues by deriving accents from the 5-band analysis instead of aborting.
- During extremely quiet or silent passages, the system still emits valid low-intensity DMX frames instead of failing or producing undefined values.
- If the user interrupts generation with Ctrl+C, the system stops cleanly and does not leave a partial output file behind.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST present a terminal-based UI listing all files matching `data/songs/*.mp3`.
- **FR-001a**: System MUST list songs based on the contents of `data/songs/*.mp3` even when required render artifacts for some songs are missing.
- **FR-002**: System MUST strip the `.mp3` extension from the displayed song names.
- **FR-003**: System MUST provide visual feedback of the currently focused item using a '▶' character on the left side.
- **FR-004**: System MUST allow navigation through the song list using the up and down cursor keys.
- **FR-005**: System MUST accept the user's selection when the 'Enter' key is pressed.
- **FR-005a**: System MUST accept an optional `--show-name` input for the output file, default to `main-show` when none is provided, and reject values that are not safe for a single filename segment. A safe show name matches `^[A-Za-z0-9_-]+$`.
- **FR-005b**: System MUST resolve per-song artifacts by matching the selected MP3 basename exactly to the `<Song - Artist>` artifact directory name.
- **FR-006**: System MUST process the selected song using an FFT analysis input that can be resolved into the canonical 5-band render model.
- **FR-006a**: System MUST require per-song beat and duration metadata for render timing and cue validation.
- **FR-007**: System MUST use exactly 5 distinct canonical energy bands to capture timbral complexity, including deterministic normalization from the supported upstream FFT layout when needed.
- **FR-008**: System MUST map the 5-band FFT energy onto a 2D virtual stage canvas.
- **FR-009**: System MUST generate and save the resulting light show as a binary DMX file.
- **FR-010**: System MUST interpret fixture positions from canonical rig inputs and apply app-specific virtual canvas metadata during rendering.
- **FR-011**: System MUST support distinct fixture behaviors for fixed washers and moving heads that target named stage points.
- **FR-012**: System MUST determine fixture sampling and targeting from configured stage coordinates and named target points.
- **FR-013**: System MUST include a procedural pattern engine (shader engine) capable of rendering geometric visualizations (e.g., linear waves, radial circular pulses) across the 2D stage canvas.
- **FR-014**: System MUST allow pattern generators to calculate intensities for any 2D coordinate based on continuous variables including time, spatial configuration (e.g., angle), and audio-driven parameters (speed, frequency).
- **FR-015**: System MUST maintain a global musical state buffer that tracks instantaneous and cumulative audio metrics, current section context, and validated cue-trigger context to provide continuous context to all pattern generators.
- **FR-015a**: System MUST apply configurable attack and release smoothing to the 5-band analysis before pattern evaluation.
- **FR-016**: System MUST support layer blending, allowing multiple procedural patterns to be composited together to form complex visual outputs.
- **FR-017**: System MUST support spatial coordinate distortion (warping), enabling audio features (e.g., mid-range energy) to dynamically shift the 2D sampling coordinates of fixtures prior to pattern evaluation.
- **FR-018**: System MUST implement specific procedural pattern types including Radial Pulses (e.g., for transient, high-energy events like drum hits) and Linear Waves (e.g., for steady, ambient frequency bands).
- **FR-019**: System MUST interpret per-song section metadata to vary rendering behavior across the song structure.
- **FR-020**: System MUST accept optional validated event cue input from the per-song event layer for discrete visual accents when that cue input is available.
- **FR-021**: System MUST fall back to transient detection from the 5-band analysis when optional event cue input is missing or invalid.
- **FR-022**: System MUST write the output file using the `{song_name}.{show_name}.dmx` naming convention.

### Key Entities

- **2D Virtual Canvas**: A spatial representation of the stage where audio energy is visualized and mapped.
- **Fixture Inputs**: The canonical rig and named-target configuration used to determine fixture placement and moving-head targets, combined with app-specific virtual canvas metadata.
- **Procedural Shader**: A mathematical model that evaluates spatio-temporal inputs (coordinates, time) alongside audio-reactive parameters to determine the visual output for a given point on the canvas.
- **Musical State Buffer**: A shared data structure (e.g., `q_buffer`) updating per-frame with derived audio metrics that is passed to all shaders, ensuring they remain musically aware across time.
- **Layer Blending Engine**: The mechanism responsible for compositing multiple active shader outputs into a single cohesive frame.
- **Song Selection State**: The index or reference of the currently highlighted and eventually selected audio track.
- **Section Metadata**: Per-song structural labels that describe where verses, choruses, drops, or other major sections occur.
- **FFT Energy Frame**: A time-sliced data structure containing 5 values representing the intensity/energy of each of the 5 frequency bands.
- **Beat and Duration Metadata**: Per-song timing metadata used as the authoritative duration source for validating cue timestamps.
- **Event Cue Input**: An optional per-song event stream that can trigger discrete visual accents when it passes validation.
- **DMX Frame**: A binary representation of the channel values for the light fixtures at a given point in time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In the default Docker environment, the CLI interface launches and renders its interactive song list within 1 second of process start.
- **SC-002**: In the default Docker environment, the system processes the standard 3-minute baseline MP3 and writes the DMX file within 60 seconds of the user confirming song selection.
- **SC-003**: The final DMX file conforms to the binary structure defined in `docs/dmx_file_specification.md`.
- **SC-004**: In the default Docker environment, the user can move the selector with the up and down arrow keys and confirm a song with Enter without navigation errors.
- **SC-005**: For the same selected song, artifact inputs, and show name, repeated runs produce identical DMX output bytes.
- **SC-006**: For any rendered frame, evaluator output maps to canonical fixture ids, numeric channel-intent values stay within DMX bounds, and moving-head targets resolve only to configured POI ids.

## Assumptions

- The application runs in an interactive terminal environment that can display a navigable song-selection interface.
- Some selectable songs may be missing required render artifacts; in that case the system still lists the song and reports the missing-input error only after selection.
- Each selectable song's artifact directory matches the song filename exactly after removing the `.mp3` extension.
- Stage rig configuration and named target points are available from existing configuration inputs.
- The canonical 5-band FFT ranges follow standard audio engineering subdivisions (e.g., Sub-bass, Bass, Low-Mid, High-Mid, High).
- The upstream `fft_bands.json` input may contain either 5 canonical values or the supported 7-band upstream layout, which is deterministically folded into the canonical 5-band model before rendering.
- The output DMX universe or channel mappings will rely on a predefined default schema if not explicitly customized.
- All target MP3 files are decoded properly  without DRM restrictions.
