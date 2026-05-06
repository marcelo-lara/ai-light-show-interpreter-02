interface MathParamsPanelProps {
  currentTime: number;
  sectionLabel: string;
  mathState: {
    bands: number[];
    intensity_hit: number;
    cumulative_rotation: number;
    mid_warp: number;
    section_label: string;
    section_progress: number;
    cue_trigger: number;
  };
}

export default function MathParamsPanel({ currentTime, sectionLabel, mathState }: MathParamsPanelProps) {
  return (
    <div className="panel card">
      <h2>Math Parameters</h2>
      <div className="metric big-time">{currentTime.toFixed(2)}s</div>
      <div className="parameter-row">
        <span>Section</span>
        <strong>{sectionLabel || mathState.section_label || "unknown"}</strong>
      </div>
      <div className="parameter-row">
        <span>Section Progress</span>
        <strong>{(mathState.section_progress * 100).toFixed(0)}%</strong>
      </div>
      <div className="parameter-row">
        <span>Band Energy</span>
        <strong>{mathState.bands.map((value) => value.toFixed(2)).join(", ")}</strong>
      </div>
      <div className="parameter-row">
        <span>Hit Intensity</span>
        <strong>{mathState.intensity_hit.toFixed(2)}</strong>
      </div>
      <div className="parameter-row">
        <span>Rotation</span>
        <strong>{mathState.cumulative_rotation.toFixed(2)}</strong>
      </div>
      <div className="parameter-row">
        <span>Warp</span>
        <strong>{mathState.mid_warp.toFixed(2)}</strong>
      </div>
      <div className="parameter-row">
        <span>Cue Trigger</span>
        <strong>{mathState.cue_trigger.toFixed(2)}</strong>
      </div>
    </div>
  );
}
