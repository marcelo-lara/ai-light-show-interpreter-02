# Data Model: Audio to DMX Generator

## 1. DMX Show Frame
**Description**: The output state of the DMX universe at a discrete slice of time (20ms) inside `/data/shows/`.
**Data Structure**:
- A linear bytearray of size $N$ (where $N = 512$ channels for 1 universe).
- Each channel is an 8-bit unsigned integer (0-255).
- Sequence of frames dictates the `.dmx` binary file length.

## 2. Global Musical State (q_buffer)
**Description**: Tracks instantaneous and cumulative audio metrics across a sequence of 5-band FFT frames.
**Fields (Python Types)**:
- `timestamp` (float): Current frame time in seconds.
- `fft_bands` (dict/array): Current 5-band smoothed energy `[sub_bass, bass, low_mid, high_mid, high]`.
- `q_transient_hit` (bool/float): Instantaneous drum/beat hit intensity.
- `q_cumulative_rotation` (float): A steadily integrating value representing ongoing ambient progression.
- `q_mid_warp` (float): Spatial distortion magnitude derived from the `low_mid` or `high_mid` band.

## 3. Fixture Virtual Canvas Schema (`stage_virtual_canvas.json`)
**Description**: The spatial layout and typing of lighting instruments on the 2D stage canvas.
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
      "dmx": {
        "start_channel": 1,
        "mapping": ["dimmer", "red", "green", "blue"]
      }
    },
    {
      "id": "moving_head_1",
      "type": "spot",
      "position": [7.5, 0.0],
      "dmx": {
        "start_channel": 10,
        "mapping": ["pan", "tilt", "dimmer", "color_wheel"] // requires targeting logic
      }
    }
  ]
}
```
**Constraints**: 
- Static washers (`washer`) only need a `position` because their beam is fixed. We evaluate the shader at that point.
- Moving heads (`spot`) can cover multiple coordinates. We determine their position based on their pan/tilt angle, or we evaluate the entire canvas and instruct moving heads to "target" high-intensity spots.
