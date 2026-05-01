# Contract: UI WebSocket API

## Overview
This contract defines the data format and communication protocol between the Python Engine (Backend) and the Canvas Output Web UI (Frontend). Due to the "Single Output Target" constitution rule, the complete canvas, meshes, and math parameters must be streamed over a WebSocket rather than written to `/data` as intermediate files.

## Connection
- **Protocol:** WebSocket (`ws://` or `wss://`)
- **Port:** `3301`
- **Endpoint:** `/ws/canvas`
- **Direction:** Bidirectional.
  - **Backend -> Frontend**: Broadcasts `loading`, `ready`, `init`, `frame`, `end`, and `error` events.
  - **Frontend -> Backend**: Sends song-selection and playback control intents (`select_song`, `play`).

## Lifecycle
1. **Selection Phase**: UI loads the available songs and sends `select_song` when the user picks one from the dropdown.
2. **Bake Phase**: Backend emits `loading`, evaluates the selected song as fast as possible, and writes the `.dmx` artifact without UI throttling.
3. **Ready Phase**: Backend sends `ready` followed by `init`. UI enables the "Play" button.
4. **Playback Phase**: User clicks "Play" in the UI. UI sends `play`. Both backend and frontend start synchronous playback (backend emits `frame` messages at 50 FPS from RAM, while UI plays audio from the static songs mount).

## Event Types

### 1. Frontend: `select_song` Event
Sent by the UI when the user changes the song dropdown.

```json
{
  "type": "select_song",
  "data": {
    "song_name": "Cinderella - Ella Lee"
  }
}
```

### 2. Backend: `loading` Event
Sent immediately after song selection and before the backend finishes baking the requested show.

```json
{
  "type": "loading",
  "data": {
    "song_name": "Cinderella - Ella Lee"
  }
}
```

### 3. Backend: `ready` Event
Sent after the `.dmx` generation completes. Signals to the UI that it can enable the "Play" button.
```json
{
  "type": "ready"
}
```

### 4. Frontend: `play` Event
Sent by the UI to tell the backend to start streaming `frame` data at 1x speed.
```json
{
  "type": "play",
  "data": {
    "start_time": 0.0
  }
}
```

### 5. Backend: `init` Event
Sent immediately after `ready` and again upon `play` to establish canvas definitions. React uses this to set up the HTML5 Canvas dimensions and initialize component state.

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

### 6. Backend: `frame` Event
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

### 7. Backend: `end` Event
Sent when a playback session ends or when an in-flight playback is cancelled because the UI selected a different song.

```json
{
  "type": "end"
}
```

### 8. Backend: `error` Event
Sent when song selection or baking fails.

```json
{
  "type": "error",
  "data": {
    "message": "Selected song is missing artifacts: Missing Song"
  }
}
```

## Styling & Theme Definitions
- **Palette**: Pure Dark Mode; Accent: `#9000dd`
- **Geometry**: `border-radius: 0` (Hard edges)
- **Density**: Compact padding (`max 0.5em`)
- **Typography**: Monospaced font for Big Time Display to prevent character jumping during playback
