# Data Model: Audio to DMX Generator

## 1. DMX Show Frame
**Description**: The output state of the DMX universe at a discrete slice of time (20ms) inside `/data/shows/{song_name}.{show_name}.dmx`.
**Data Structure**:
- A frame record containing a 4-byte timestamp followed by a linear bytearray of size $N$ (where $N = 512$ channels for 1 universe).
- Each channel is an 8-bit unsigned integer (0-255).
- Sequence of frame records follows a fixed binary header and dictates the `.dmx` file length.

## 2. FFT Energy Input
**Description**: The canonical per-song 5-band analysis input used to drive the musical state.
**Source**:
- `data/artifacts/<Song - Artist>/essentia/fft_bands.json`
**Constraints**:
- The file is read-only input produced by an upstream pipeline.
- Each frame resolves to exactly 5 ordered energy values for the selected song.
- The `<Song - Artist>` directory name matches the selected MP3 basename with the `.mp3` extension removed.

## 3. Beat and Duration Metadata Input
**Description**: The canonical timing metadata used for render timing, beat alignment, and cue-duration validation.
**Source**:
- `data/artifacts/<Song - Artist>/essentia/beats.json`
**Example Shape**:
```json
{
  "duration": 183.42,
  "bpm": 124.0,
  "beats": [
    {"time": 0.0, "bar": 1, "beat_in_bar": 1},
    {"time": 0.48, "bar": 1, "beat_in_bar": 2}
  ]
}
```
**Constraints**:
- `duration` is the authoritative song duration for validating cue timestamps.
- `beats[]` provides the shared timing grid used by render logic.

## 4. Section Metadata Input
**Description**: The canonical per-song section structure input used to vary rendering behavior across verses, choruses, drops, and other major song regions.
**Source**:
- `data/artifacts/<Song - Artist>/section_segmentation/sections.json`
**Constraints**:
- The file is read-only input produced by an upstream pipeline.
- Section boundaries and labels are treated as required render context for section-aware behavior.

## 5. Global Musical State (q_buffer)
**Description**: Tracks instantaneous and cumulative audio metrics across a sequence of 5-band FFT frames.
**Fields (Python Types)**:
- `time` (float): Current frame time in seconds.
- `bands` (array): Current 5-band smoothed energy `[sub_bass, bass, low_mid, high_mid, high]`.
- `intensity_hit` (float): Instantaneous drum or beat hit intensity.
- `cumulative_rotation` (float): A steadily integrating value representing ongoing ambient progression.
- `mid_warp` (float): Spatial distortion magnitude derived from the `low_mid` or `high_mid` band.
- `section_label` (string): Current song section label derived from `sections.json`.
- `section_progress` (float): Normalized progress through the current section from 0.0 to 1.0.
- `cue_trigger` (float): A normalized accent strength derived from validated event cues or transient fallback logic.

## 6. Event Cue Input
**Description**: Optional per-song event data used to trigger discrete visual accents.
**Source**:
- `data/artifacts/<Song - Artist>/lighting_events.json`
**Example Shape**:
```json
{
  "cue_anchors": [
    {"id": "chorus_hit_1", "time": 42.16, "label": "chorus_hit"}
  ],
  "lighting_events": [
    {"time": 42.16, "anchor_id": "chorus_hit_1", "strength": 0.9, "type": "accent"}
  ]
}
```
**Constraints**:
- The file is advisory, not required.
- A minimally valid cue record contains `time`, `type`, and either `anchor_id` or a resolvable cue anchor reference.
- Event cue data is only considered valid when it parses successfully and its cue timestamps are monotonically increasing within the selected song duration reported by `data/artifacts/<Song - Artist>/essentia/beats.json`.
- If any cue record is malformed, the system ignores the event-cue file for that song and falls back to transient detection rather than attempting partial ingestion.
- Invalid or missing event cue data must trigger fallback to transient detection from FFT energy rather than aborting the render.

## 7. Fixture Render State
**Description**: The per-frame render intent emitted by the evaluator before fixture-template channel packing.
**Fields**:
- `fixture_id` (string): Canonical fixture instance id from `data/fixtures/fixtures.json`.
- `dimmer` (int): Final brightness value from 0 to 255.
- `color_rgb` (array): Final RGB triplet for fixtures with color mixing.
- `target_poi` (string|null): Named POI id for moving heads; `null` for fixed washers.
**Constraints**:
- This structure is the handoff boundary between the evaluator and the DMX writer.
- The DMX writer maps these values onto actual channel addresses using canonical fixture/template metadata.
- The evaluator consumes section-aware and cue-aware musical state when generating this structure.
- `fixture_id` in the render state MUST equal `source_fixture_id` from the derived virtual-canvas entry rather than the local virtual-canvas `id`.

## 8. Fixture Virtual Canvas Schema (`stage_virtual_canvas.json`)
**Description**: App-specific render metadata layered on top of canonical rig and POI inputs for the 2D stage canvas.
**Fields**:
```json
{
  "canvas": {
    "width": 10.0,  // meters
    "height": 5.0   // meters
  },
  "fixtures": [
    {
      "id": "parcan_pl",
      "type": "washer",
      "position": [2.0, 0.5], // x, y
      "source_fixture_id": "parcan_pl",
      "group": "washers"
    },
    {
      "id": "parcan_l",
      "type": "washer",
      "position": [4.0, 0.0],
      "source_fixture_id": "parcan_l",
      "group": "washers"
    },
    {
      "id": "parcan_r",
      "type": "washer",
      "position": [6.0, 0.0],
      "source_fixture_id": "parcan_r",
      "group": "washers"
    },
    {
      "id": "parcan_pr",
      "type": "washer",
      "position": [8.0, 0.5],
      "source_fixture_id": "parcan_pr",
      "group": "washers"
    },
    {
      "id": "mini_beam_prism_r",
      "type": "moving_head",
      "position": [9.85, 1.0],
      "target_poi": "wall_art_right",
      "source_fixture_id": "mini_beam_prism_r",
      "group": "moving_heads"
    }
  ]
}
```
**Constraints**: 
- `data/fixtures/fixtures.json` remains the canonical source of fixture identity, DMX base channels, and physical locations.
- `data/fixtures/pois.json` remains the canonical source of named target points for moving heads.
- `stage_virtual_canvas.json` must not duplicate canonical DMX channel ownership.
- The local virtual-canvas `id` is render metadata only; canonical fixture identity is always carried by `source_fixture_id`.
- Canonical fixture coordinates normalized to the 0..1 range are mapped onto the 10x5 virtual canvas by linear scaling: `canvas_x = normalized_x * 10.0`, `canvas_y = normalized_y * 5.0`.
- Static washers (`washer`) only need a fixed sample `position` because their beam is treated as stationary in v1.
- Moving heads (`moving_head`) target named POIs in v1 rather than performing dynamic brightest-region search.
