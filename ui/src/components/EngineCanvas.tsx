import { useEffect, useMemo, useRef } from "react";

interface EngineCanvasProps {
  canvasConfig: {
    width: number;
    height: number;
  };
  mesh: {
    resolution: [number, number];
    pixels: number[][][];
  } | null;
  fixtures: Array<{
    id: string;
    position: [number, number];
    type: string;
  }>;
  currentTime: number;
}

export default function EngineCanvas({ canvasConfig, mesh, fixtures, currentTime }: EngineCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const width = 780;
  const height = 390;

  const canvasRatio = useMemo(() => {
    return canvasConfig.width && canvasConfig.height
      ? canvasConfig.width / canvasConfig.height
      : 2;
  }, [canvasConfig.width, canvasConfig.height]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !mesh) {
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return;
    }

    const [cols, rows] = mesh.resolution;
    const cellWidth = width / cols;
    const cellHeight = height / rows;

    mesh.pixels.forEach((row, rowIndex) => {
      row.forEach((pixel, colIndex) => {
        ctx.fillStyle = `rgb(${pixel[0]}, ${pixel[1]}, ${pixel[2]})`;
        ctx.fillRect(colIndex * cellWidth, rowIndex * cellHeight, cellWidth, cellHeight);
      });
    });

    fixtures.forEach((fixture) => {
      const x = (fixture.position[0] / canvasConfig.width) * width;
      const y = (fixture.position[1] / canvasConfig.height) * height;
      ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
      ctx.fillRect(x - 4, y - 4, 8, 8);
      ctx.strokeStyle = "#9000dd";
      ctx.lineWidth = 1;
      ctx.strokeRect(x - 5, y - 5, 10, 10);
    });

    ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= cols; i += 1) {
      ctx.beginPath();
      ctx.moveTo(i * cellWidth, 0);
      ctx.lineTo(i * cellWidth, height);
      ctx.stroke();
    }
    for (let i = 0; i <= rows; i += 1) {
      ctx.beginPath();
      ctx.moveTo(0, i * cellHeight);
      ctx.lineTo(width, i * cellHeight);
      ctx.stroke();
    }
  }, [canvasConfig.width, canvasConfig.height, fixtures, mesh]);

  return (
    <div className="panel canvas-card">
      <div className="canvas-header">
        <div>Canvas Output</div>
        <div className="time-display">{currentTime.toFixed(2)}s</div>
      </div>
      <canvas className="engine-canvas" ref={canvasRef} width={width} height={height} />
    </div>
  );
}
