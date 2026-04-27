# Feature Specification: Audio to DMX Generator with CLI

**Feature Branch**: `001-fft-dmx-generator`  
**Created**: 2026-04-27
**Status**: Ready for Planning  
**Input**: User description: "CLI-UI the entrypoint of this python application should be a list of the songs from data/songs/*.mp3 without the file extension. an '▶' should be on the left of each song item, and use the cursor keys to move between songs, and 'enter' to select a song. As a performer, I want my lights to react to 5-band FFT energy so that the visual intensity matches the timbral complexity of my music. at the end, I need to have a binary DMX file to perform the show."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Song Selection via CLI (Priority: P1)

As a user, I want to launch the application and see a list of my songs so that I can easily select which song to process for my light show.

**Why this priority**: It is the primary entrypoint for the application and is required before any processing can occur.

**Independent Test**: Can be fully tested by launching the CLI, observing the list of mp3 files from `data/songs/`, navigating with arrow keys, and pressing enter to confirm a selection.

**Acceptance Scenarios**:

1. **Given** the `data/songs/` directory contains mp3 files, **When** I run the entrypoint, **Then** I see the list of song names without the `.mp3` extension.
2. **Given** the song list is displayed, **When** I use the up/down cursor keys, **Then** an '▶' indicator moves to the currently highlighted song.
3. **Given** a song is highlighted with the '▶' indicator, **When** I press 'Enter', **Then** the application selects this song for processing.

---

### User Story 2 - Audio Processing to DMX Generation (Priority: P1)

As a performer, I want the system to analyze the selected song using a 5-band FFT, and output a binary DMX file so that my lights react proportionally to the song's timbral complexity during my show.

**Why this priority**: This provides the core value of translating the music into the required physical output format (DMX) for performance.

**Independent Test**: Can be fully tested by processing an MP3 file and validating that a binary DMX output file is created and contains control data synchronized to the audio.

**Acceptance Scenarios**:

1. **Given** a song has been selected and its 5-band analysis is available, **When** the application processes it, **Then** it uses exactly 5 energy bands to drive the light show.
2. **Given** the 5-band energy is available, **When** generating the light show, **Then** the visual intensity changes in proportion to those energy levels.
3. **Given** the processing is complete, **When** the application finishes, **Then** a binary DMX show file is produced for use in the performance.

### Edge Cases

- If the song directory is empty or missing, the system shows a clear message and exits without starting processing.
- If the selected song or its required analysis inputs are unreadable or invalid, the system aborts with a clear error and does not write a partial show file.
- During extremely quiet or silent passages, the system still emits valid low-intensity DMX frames instead of failing or producing undefined values.
- If the user interrupts generation with Ctrl+C, the system stops cleanly and does not leave a partial output file behind.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST present a terminal-based UI listing all files matching `data/songs/*.mp3`.
- **FR-002**: System MUST strip the `.mp3` extension from the displayed song names.
- **FR-003**: System MUST provide visual feedback of the currently focused item using a '▶' character on the left side.
- **FR-004**: System MUST allow navigation through the song list using the up and down cursor keys.
- **FR-005**: System MUST accept the user's selection when the 'Enter' key is pressed.
- **FR-006**: System MUST process the selected song using an available 5-band FFT analysis.
- **FR-007**: System MUST use exactly 5 distinct energy bands to capture timbral complexity.
- **FR-008**: System MUST map the 5-band FFT energy onto a 2D virtual stage canvas.
- **FR-009**: System MUST generate and save the resulting light show as a binary DMX file.
- **FR-010**: System MUST interpret fixture positions and stage metadata from configuration inputs representing the virtual stage canvas.
- **FR-011**: System MUST support distinct fixture behaviors for fixed washers and moving heads that target named stage points.
- **FR-012**: System MUST determine fixture sampling and targeting from configured stage coordinates and named target points.
- **FR-013**: System MUST include a procedural pattern engine (shader engine) capable of rendering geometric visualizations (e.g., linear waves, radial circular pulses) across the 2D stage canvas.
- **FR-014**: System MUST allow pattern generators to calculate intensities for any 2D coordinate based on continuous variables including time, spatial configuration (e.g., angle), and audio-driven parameters (speed, frequency).
- **FR-015**: System MUST maintain a global musical state buffer that tracks instantaneous and cumulative audio metrics (e.g., hit intensity, cumulative rotation) to provide continuous context to all pattern generators.
- **FR-016**: System MUST support layer blending, allowing multiple procedural patterns to be composited together to form complex visual outputs.
- **FR-017**: System MUST support spatial coordinate distortion (warping), enabling audio features (e.g., mid-range energy) to dynamically shift the 2D sampling coordinates of fixtures prior to pattern evaluation.
- **FR-018**: System MUST implement specific procedural pattern types including Radial Pulses (e.g., for transient, high-energy events like drum hits) and Linear Waves (e.g., for steady, ambient frequency bands).

### Key Entities

- **2D Virtual Canvas**: A spatial representation of the stage where audio energy is visualized and mapped.
- **Fixture Manifest**: A configuration schema (`stage_virtual_canvas.json`) containing the 2D placement and types of lighting fixtures across the space.
- **Procedural Shader**: A mathematical model that evaluates spatio-temporal inputs (coordinates, time) alongside audio-reactive parameters to determine the visual output for a given point on the canvas.
- **Musical State Buffer**: A shared data structure (e.g., `q_buffer`) updating per-frame with derived audio metrics that is passed to all shaders, ensuring they remain musically aware across time.
- **Layer Blending Engine**: The mechanism responsible for compositing multiple active shader outputs into a single cohesive frame.
- **Song Selection State**: The index or reference of the currently highlighted and eventually selected audio track.
- **FFT Energy Frame**: A time-sliced data structure containing 5 values representing the intensity/energy of each of the 5 frequency bands.
- **DMX Frame**: A binary representation of the channel values for the light fixtures at a given point in time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The CLI interface launches and is interactive within 1 second of execution.
- **SC-002**: The system successfully processes a standard 3-minute MP3 file and generates a DMX file within a reasonable offline timeframe (e.g., under 60 seconds).
- **SC-003**: The final DMX file conforms to the structural requirements of binary DMX data format capable of being playback by standard controllers.
- **SC-004**: Users are able to visually identify and select a song without encountering navigation errors.

## Assumptions

- The application runs in an interactive terminal environment that can display a navigable song-selection interface.
- Each selectable song has a corresponding precomputed 5-band analysis input available to the system.
- Stage rig configuration and named target points are available from existing configuration inputs.
- The 5-band FFT ranges will follow standard audio engineering subdivisions (e.g., Sub-bass, Bass, Low-Mid, High-Mid, High) unless specified otherwise.
- The output DMX universe or channel mappings will rely on a predefined default schema if not explicitly customized.
- All target MP3 files are decoded properly  without DRM restrictions.
