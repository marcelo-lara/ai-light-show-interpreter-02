# Documentation

This folder contains detailed documentation, specifications, and schemas for the `ai-light-show-interpreter-02` rendering engine.

## Contents

* **Schemas:** JSON schemas or structural interface definitions for input/output data (e.g., Virtual Canvas format, parsed specific FFT band data).
* **Architecture:** In-depth technical details on the baking and rasterization pipeline.
* **Math Patterns:** Documentation for the mathematical functions used to generate the stage visuals (e.g., simplex noise, sine waves, blending modes).
* **UI Runtime:** The browser inspection UI is served by the Dockerized Vite service on port `3300` and connects to the backend WebSocket on port `3301` for `ready`, `init`, `frame`, `end`, and `error` events.