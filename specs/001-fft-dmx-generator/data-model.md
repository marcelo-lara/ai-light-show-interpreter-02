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

## 3. Global Musical State (q_buffer)
**Description**: Tracks instantaneous and cumulative audio metrics across a sequence of 5-band FFT frames.
**Fields (Python Types)**:
- `time` (float): Current frame time in seconds.
- `bands` (array): Current 5-band smoothed energy `[sub_bass, bass, low_mid, high_mid, high]`.
- `intensity_hit` (float): Instantaneous drum or beat hit intensity.
- `cumulative_rotation` (float): A steadily integrating value representing ongoing ambient progression.
- `mid_warp` (float): Spatial distortion magnitude derived from the `low_mid` or `high_mid` band.

## 4. Fixture Virtual Canvas Schema (`stage_virtual_canvas.json`)
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
      "id": "parcan_1",
      "type": "washer",
      "position": [2.5, 5.0], // x, y
      "source_fixture_id": "wash_stage_left",
      "dmx": {
        "start_channel": 1,
        "mapping": ["dimmer", "red", "green", "blue"]
      }
    },
    {
      "id": "moving_head_1",
      "type": "moving_head",
      "position": [7.5, 0.0],
      "target_poi": "center_stage",
      "source_fixture_id": "mini_beam_prism_l",
      "dmx": {
        "start_channel": 10,
        "mapping": ["pan", "tilt", "dimmer", "color_wheel"] // requires targeting logic
      }
    }
  ]
}
```
**Constraints**: 
- `data/fixtures/fixtures.json` remains the canonical source of fixture identity, DMX base channels, and physical locations.
- `data/fixtures/pois.json` remains the canonical source of named target points for moving heads.
- Static washers (`washer`) only need a fixed sample `position` because their beam is treated as stationary in v1.
- Moving heads (`moving_head`) target named POIs in v1 rather than performing dynamic brightest-region search.
