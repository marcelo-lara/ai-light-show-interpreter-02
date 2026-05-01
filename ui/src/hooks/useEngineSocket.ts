import { useEffect, useRef, useState } from "react";

interface EngineState {
  songName: string | null;
  duration: number;
  canvas: { width: number; height: number };
  fixtures: Array<{
    id: string;
    position: [number, number];
    type: string;
    dimmer?: number;
    color_rgb?: [number, number, number];
  }>;
  qBuffer: {
    bands: number[];
    intensity_hit: number;
    cumulative_rotation: number;
    mid_warp: number;
    section_label: string;
    section_progress: number;
    cue_trigger: number;
  };
  canvasMesh: { resolution: [number, number]; pixels: number[][][] } | null;
  time: number;
  sectionLabel: string;
  ready: boolean;
}

const initialState: EngineState = {
  songName: null,
  duration: 0,
  canvas: { width: 10, height: 5 },
  fixtures: [],
  qBuffer: {
    bands: [0, 0, 0, 0, 0],
    intensity_hit: 0,
    cumulative_rotation: 0,
    mid_warp: 0,
    section_label: "unknown",
    section_progress: 0,
    cue_trigger: 0,
  },
  canvasMesh: null,
  time: 0,
  sectionLabel: "unknown",
  ready: false,
};

export function useEngineSocket() {
  const [state, setState] = useState<EngineState>(initialState);
  const [status, setStatus] = useState("connecting...");

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);

  useEffect(() => {
    let disposed = false;

    const clearReconnectTimer = () => {
      if (reconnectTimerRef.current !== null) {
        window.clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };

    const scheduleReconnect = () => {
      if (disposed || reconnectTimerRef.current !== null) {
        return;
      }
      reconnectTimerRef.current = window.setTimeout(() => {
        reconnectTimerRef.current = null;
        connect();
      }, 1000);
    };

    const connect = () => {
      clearReconnectTimer();
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const socketUrl = `${protocol}://${window.location.hostname}:3301/ws/canvas`;
      const socket = new WebSocket(socketUrl);
      socketRef.current = socket;
      setStatus("connecting...");

      socket.addEventListener("open", () => {
        setStatus((current) => (current === "ready" ? current : "connected"));
      });

      socket.addEventListener("message", (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "ready") {
          setState((current) => ({ ...current, ready: true }));
          setStatus("ready");
        }
        if (data.type === "init") {
          const payload = data.data;
          setState((current) => ({
            ...current,
            songName: payload.song_name,
            duration: payload.duration,
            canvas: payload.canvas,
            fixtures: payload.fixtures,
          }));
        }
        if (data.type === "frame") {
          const payload = data.data;
          const renderStates = new Map(
            (payload.fixtures as Array<{ id: string; dimmer?: number; color_rgb?: [number, number, number] }>).map(
              (fixture) => [fixture.id, fixture],
            ),
          );
          setState((current) => ({
            ...current,
            time: payload.time,
            qBuffer: payload.q_buffer,
            fixtures: current.fixtures.map((fixture) => ({
              ...fixture,
              ...renderStates.get(fixture.id),
            })),
            canvasMesh: payload.canvas_mesh,
            sectionLabel: payload.q_buffer.section_label,
          }));
        }
        if (data.type === "end") {
          setStatus("finished");
        }
      });

      socket.addEventListener("close", () => {
        socketRef.current = null;
        setStatus((current) => (current === "finished" ? current : "disconnected"));
        scheduleReconnect();
      });

      socket.addEventListener("error", () => {
        setStatus("error");
      });
    };

    connect();

    return () => {
      disposed = true;
      clearReconnectTimer();
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, []);

  const sendPlay = (startTime: number) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      setStatus("disconnected");
      return;
    }
    socketRef.current.send(JSON.stringify({ type: "play", data: { start_time: startTime } }));
  };

  return { state, status, sendPlay };
}
