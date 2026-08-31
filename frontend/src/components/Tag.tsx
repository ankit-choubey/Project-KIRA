import React from "react";
import type { TagClassification } from "../data/metrics.registry";
import { LockIcon } from "./SvgIcons";

interface TagProps {
  classification: TagClassification;
  onClick?: (e: React.MouseEvent) => void;
  clickable?: boolean;
  className?: string;
}

export const Tag: React.FC<TagProps> = ({
  classification,
  onClick,
  clickable = true,
  className = "",
}) => {
  const getTagStyleClass = () => {
    switch (classification) {
      case "MEASURED":
        return "tag-measured";
      case "EXP-007-A":
      case "EXP-007-B":
      case "EXP-007-C":
      case "EXP-007-D":
      case "EXP-007-E":
      case "EXP-007-F":
      case "EXP-007-G":
      case "EXP-007-H":
        return "tag-exp";
      case "REAL-WORLD DATA":
        return "tag-realworld";
      case "FAILURE FINDING":
        return "tag-failure";
      case "SMALL SAMPLE":
        return "tag-smallsample";
      case "LOOPBACK BENCHMARK":
        return "tag-loopback";
      case "LIVE":
        return "tag-live";
      case "SHA-256 VERIFIED":
        return "tag-sha";
      default:
        return "tag-default";
    }
  };

  const isInteractive = clickable && !!onClick;

  return (
    <button
      type="button"
      className={`provenance-tag ${getTagStyleClass()} ${isInteractive ? "interactive" : ""} ${className}`}
      onClick={isInteractive ? onClick : undefined}
      title={isInteractive ? "Click to view provenance and experiment evidence" : undefined}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "4px",
        fontFamily: "var(--font-mono)",
        fontSize: "10.5px",
        fontWeight: 600,
        letterSpacing: "0.04em",
        padding: "2px 7px",
        borderRadius: "var(--radius-sm)",
        textTransform: "uppercase",
        border: "1px solid transparent",
        cursor: isInteractive ? "pointer" : "default",
        background: "transparent",
      }}
    >
      {classification === "LIVE" && <span className="live-dot" />}
      {classification === "SHA-256 VERIFIED" && <LockIcon size={11} />}
      <span>{classification}</span>
    </button>
  );
};
