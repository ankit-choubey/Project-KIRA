import React from "react";
import { Metric } from "./Metric";
import { METRIC_REGISTRY } from "../data/metrics.registry";

interface StatTileProps {
  metricId: string;
  subtitle?: string;
  highlight?: "neutral" | "allow" | "warn" | "block";
  digits?: number;
  className?: string;
}

export const StatTile: React.FC<StatTileProps> = ({
  metricId,
  subtitle,
  highlight = "neutral",
  digits,
  className = "",
}) => {
  const spec = METRIC_REGISTRY[metricId];

  return (
    <div className={`card stat-tile highlight-${highlight} ${className}`}>
      <div className="stat-tile-header">
        <span className="stat-tile-label">{spec?.label || metricId}</span>
      </div>

      <div className="stat-tile-body">
        <Metric id={metricId} digits={digits} />
      </div>

      {(subtitle || spec?.scope) && (
        <div className="stat-tile-footer">
          <span className="stat-tile-subtext">
            {subtitle || spec?.scope}
          </span>
        </div>
      )}
    </div>
  );
};
