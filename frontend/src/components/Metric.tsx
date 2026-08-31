import React, { useState } from "react";
import { METRIC_REGISTRY, extractJsonPath, type MetricSpec } from "../data/metrics.registry";
import { useArtifact } from "../data/useArtifact";
import { fmt, fmtPercent, fmtInt, fmtMs, fmtFloat, fmtSec, isNullOrUndefined } from "../data/format";
import { Tag } from "./Tag";
import { EvidenceDrawer } from "./EvidenceDrawer";

interface MetricProps {
  id: string;
  digits?: number;
  showTag?: boolean;
  className?: string;
  renderValueOnly?: boolean;
  overrideValue?: number | null;
}

export const Metric: React.FC<MetricProps> = ({
  id,
  digits,
  showTag = true,
  className = "",
  renderValueOnly = false,
  overrideValue,
}) => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const spec: MetricSpec | undefined = METRIC_REGISTRY[id];

  // If metric is not in registry, render honest fallback
  if (!spec) {
    return <span className="unmeasured">unregistered metric ({id})</span>;
  }

  const { data, loading, missing } = useArtifact(spec.artifact);

  let rawValue: any = overrideValue !== undefined ? overrideValue : extractJsonPath(data, spec.path);
  const precision = digits ?? spec.digits;

  const formatValue = (v: any): string => {
    if (loading) return "…";
    if (missing || isNullOrUndefined(v)) return "not measured";

    const num = typeof v === "number" ? v : parseFloat(v);
    if (isNaN(num)) return String(v);

    switch (spec.format) {
      case "percent":
        return fmtPercent(num, precision ?? 2);
      case "int":
        return fmtInt(num);
      case "ms":
        return fmtMs(num, precision ?? 2);
      case "sec":
        return fmtSec(num, precision ?? 2);
      case "float":
        return fmtFloat(num, precision ?? 4);
      default:
        return fmt(num, precision ?? 3);
    }
  };

  const formatted = formatValue(rawValue);
  const isUnmeasured = formatted === "not measured";

  if (renderValueOnly) {
    return (
      <span className={`tabular ${isUnmeasured ? "unmeasured" : ""} ${className}`}>
        {formatted}
      </span>
    );
  }

  return (
    <>
      <div className={`metric-badge-container ${className}`}>
        <span
          className={`metric-val tabular ${isUnmeasured ? "unmeasured" : ""}`}
          onClick={() => setDrawerOpen(true)}
          style={{ cursor: "pointer" }}
        >
          {formatted}
        </span>
        {showTag && (
          <Tag
            classification={spec.classification}
            onClick={() => setDrawerOpen(true)}
          />
        )}
      </div>

      {drawerOpen && (
        <EvidenceDrawer
          spec={spec}
          rawValue={rawValue}
          formattedValue={formatted}
          onClose={() => setDrawerOpen(false)}
        />
      )}
    </>
  );
};
