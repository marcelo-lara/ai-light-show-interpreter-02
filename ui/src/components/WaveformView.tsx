import { useEffect, useRef } from "react";
import WaveSurfer from "wavesurfer.js";

interface WaveformViewProps {
  audioUrl: string | null;
  isPlaying: boolean;
}

export default function WaveformView({ audioUrl, isPlaying }: WaveformViewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const waveRef = useRef<WaveSurfer | null>(null);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    waveRef.current = WaveSurfer.create({
      container: containerRef.current,
      waveColor: "#444",
      progressColor: "#9000dd",
      cursorColor: "#ffffff",
      barWidth: 2,
      barHeight: 1.5,
      barGap: 2,
      height: 120,
      normalize: true,
      responsive: true,
    });

    return () => {
      waveRef.current?.destroy();
      waveRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!waveRef.current || !audioUrl) {
      return;
    }

    const wavesurfer = waveRef.current;
    const handleReady = () => {
      if (isPlaying) {
        wavesurfer.play();
      }
    };

    wavesurfer.on("ready", handleReady);
    wavesurfer.load(audioUrl);

    return () => {
      wavesurfer.un("ready", handleReady);
    };
  }, [audioUrl, isPlaying]);

  useEffect(() => {
    if (!waveRef.current) {
      return;
    }
    if (isPlaying) {
      waveRef.current.play();
    } else {
      waveRef.current.pause();
    }
  }, [isPlaying]);

  return <div className="waveform-container" ref={containerRef} />;
}
