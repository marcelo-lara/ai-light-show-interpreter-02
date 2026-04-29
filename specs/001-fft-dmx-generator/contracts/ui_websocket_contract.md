# Contract: UI WebSocket API

## Overview
This contract defines the data format and communication protocol between the Python Engine (Backend) and the Canvas Output Web UI (Frontend). Due to the "Single Output Target" constitution rule, the complete canvas, meshes, and math parameters must be streamed over a WebSocket rather than written to `/data` as intermediate files.

## Connection
- **Protocol:** WebSocket (`ws://` or `wss://`)
- **Port:** `3301`
- **Endpoint:** `/ws/canvas`
- **Direction:** Bidirectional.
  - **Backend -> Frontend**: Broadcasts `ready`, `init`, `frame`, and `end` events.
  - **Frontend -> Backend**: Sends playback control intents (e.g., `play`).

## Lifecycle
1. **Bake Phase**: Backend evaluates the entire song as fast as possible to generate the `.dmx` artifact without UI throttling.
2. **Ready Phase**: Backend sends a `ready` event. UI enables the "Play" button.
3. **Playback Phase**: User clicks "Play" in the UI. UI sends `play` intent. Both backend and frontend start synchronous playback (backend emits `frame` messages at 50FPS from RAM or recalculates lazily at 1x speed to stream, while UI plays audio from static mount).

## Event Types

### 1. Backend: `ready` Event
Sent after the `.dmx` generation completes. Signals to the UI that it can enable the "Play" button.
```json
{
  "type": "ready"
}
```

### 2. Frontend: `play` Event
Sent by the UI to tell the backend to start streaming `frame` data at 1x speed.
```json
{
  "type": "play",
  "data": {
    "start_time": 0.0
  }
}
```

### 3. Backend: `init` Event
Sent immediately after `ready` or upon `play` to establish canvas definitions. React will use this to set up the HTML5 Canvas dimensions and initialize React component state.

```json
{
  "type": "init",
  "data": {
    "song_name": "The_Artist_-_The_Track",
    "duration": 183.42,
    "canvas": {
      "width": 10.0,
      "height": 5.0
    },
    "fixtures": [
      {
        "id": "parcan_l",
        "position": [4.0, 0.0],
        "type": "washer"
      }
    ]
  }
}
```

### 2. `frame` Event
Sent at 50 FPS (every 20ms) detailing the exact mathematical state of the shaders and the output of the fixtures.

```json
{
  "type": "frame",
  "data": {
    "time": 42.16,
    "q_buffer": {
      "bands": [0.1, 0.4, 0.6, 0.2, 0.8],
      "intensity_hit": 0.95,
      "cumulative_rotation": 3.14,
      "mid_warp": 0.2,
      "section_label": "chorus"
    },
    "fixtures": [
      {
        "id": "parcan_l",
        "dimmer": 255,
        "color_rgb": [255, 0, 128]
      }
    ],
    "canvas_mesh": {
      "resolution": [20, 10], 
      "pixels": [
         [255, 0, 128], [255, 10, 100], 
         ... // Rendered directly by the React HTML5 Canvas component GPU 
      ]
    }
  }
}
```
*Note:* The `canvas_mesh.pixels` array is a heavily downsampled 2D representation (e.g., 20x10) of the NumPy evaluation grid, allowing the UI to render the "full canvas with the meshes applied" efficiently.

### 3. `end` Event
Sent when the generation has concluded successfully.

```json
{
  "type": "end"
}
```

## Styling & Theme Definitions
- **Palette**: Pure Dark Mode; Accent: `#9000dd`
- **Geometry**: `border-radius: 0` (Hard edges)
- **Density**: Compact padding (`max 0.5em`)
- **Typography**: Monospaced font for Big Time Display to prevent character jumping during playback
