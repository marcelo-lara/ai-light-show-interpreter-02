import { useEffect, useMemo, useState } from "react";
import { useEngineSocket } from "./hooks/useEngineSocket";
import WaveformView from "./components/WaveformView";
import MathParamsPanel from "./components/MathParamsPanel";
import EngineCanvas from "./components/EngineCanvas";

export default function App() {
  const [playing, setPlaying] = useState(false);
  const { state, sendPlay, status } = useEngineSocket();

  const audioUrl = useMemo(() => {
    if (!state.songName) {
      return null;
    }
    return `/songs/${state.songName}.mp3`;
  }, [state.songName]);

  const handlePlay = () => {
    if (!state.ready || !audioUrl) {
      return;
    }
    setPlaying(true);
    sendPlay(0.0);
  };

  useEffect(() => {
    if (status === "finished") {
      setPlaying(false);
    }
  }, [status]);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <div className="logo">Canvas Output</div>
          <div className="song-name">{state.songName || "Waiting for song..."}</div>
        </div>
        <div className="status-pill">{status}</div>
      </header>

      <section className="hero">
        <div className="hero-left">
          <div className="hero-title">Playback Inspection</div>
          <div className="hero-subtitle">View the engine output through canvas and math state.</div>
        </div>
      </section>

      <div className="controls-row">
        <button className="action-button" onClick={handlePlay} disabled={!state.ready || !audioUrl || playing}>
          {playing ? "Playing..." : "Play"}
        </button>
        <div className="control-meta">Audio source: {audioUrl ?? "waiting for backend..."}</div>
      </div>

      <div className="content-grid">
        <aside className="sidebar">
          <MathParamsPanel mathState={state.qBuffer} currentTime={state.time} sectionLabel={state.sectionLabel} />
        </aside>
        <main className="canvas-pane">
          <EngineCanvas
            canvasConfig={state.canvas}
            mesh={state.canvasMesh}
            fixtures={state.fixtures}
            currentTime={state.time}
          />
        </main>
      </div>

      <div className="waveform-row">
        <WaveformView audioUrl={audioUrl} isPlaying={playing} />
      </div>
    </div>
  );
}
