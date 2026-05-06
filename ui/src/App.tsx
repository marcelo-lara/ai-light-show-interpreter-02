import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import { useEngineSocket } from "./hooks/useEngineSocket";
import WaveformView from "./components/WaveformView";
import MathParamsPanel from "./components/MathParamsPanel";
import EngineCanvas from "./components/EngineCanvas";

type SongOption = {
  fileName: string;
  stem: string;
};

export default function App() {
  const [playing, setPlaying] = useState(false);
  const [songs, setSongs] = useState<SongOption[]>([]);
  const [selectedSong, setSelectedSong] = useState("");
  const { state, sendPlay, sendSelectSong, status } = useEngineSocket();

  useEffect(() => {
    const controller = new AbortController();

    const loadSongs = async () => {
      try {
        const response = await fetch("/api/songs", { signal: controller.signal });
        if (!response.ok) {
          throw new Error(`Failed to load songs: ${response.status}`);
        }
        const payload = (await response.json()) as { songs?: SongOption[] };
        setSongs(Array.isArray(payload.songs) ? payload.songs : []);
      } catch (error) {
        if ((error as DOMException).name === "AbortError") {
          return;
        }
        console.error(error);
        setSongs([]);
      }
    };

    void loadSongs();

    return () => {
      controller.abort();
    };
  }, []);

  useEffect(() => {
    if (state.songName) {
      setSelectedSong(state.songName);
      return;
    }

    setSelectedSong((current) => {
      if (current && songs.some((song) => song.stem === current)) {
        return current;
      }
      return "";
    });
  }, [songs, state.songName]);

  const activeSong = state.songName ?? (selectedSong || null);

  const activeSongFileName = useMemo(() => {
    if (!activeSong) {
      return null;
    }
    return songs.find((song) => song.stem === activeSong)?.fileName ?? `${activeSong}.mp3`;
  }, [activeSong, songs]);

  const audioUrl = useMemo(() => {
    if (!activeSongFileName) {
      return null;
    }
    return `/songs/${encodeURIComponent(activeSongFileName)}`;
  }, [activeSongFileName]);

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

  const handleSongChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const nextSong = event.target.value;
    setSelectedSong(nextSong);
    setPlaying(false);
    if (nextSong) {
      sendSelectSong(nextSong);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <div className="logo">Canvas Output</div>
          {songs.length > 0 ? (
            <select
              className="song-select"
              value={activeSong ?? ""}
              onChange={handleSongChange}
              disabled={status === "loading..."}
              aria-label="Available songs"
            >
              <option value="">Select a song</option>
              {songs.map((song) => (
                <option key={song.fileName} value={song.stem}>
                  {song.stem}
                </option>
              ))}
            </select>
          ) : (
            <div className="song-name">No songs available</div>
          )}
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
        <div className="control-meta">Audio source: {audioUrl ?? "waiting for song selection..."}</div>
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
