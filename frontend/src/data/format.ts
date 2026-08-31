/**
 * Numeric and Metric Formatting Utilities
 * Enforces strict scientific presentation: null is rendered as "not measured", NEVER as "0".
 */

export function isNullOrUndefined(val: unknown): boolean {
  return val === null || val === undefined;
}

export function fmt(
  v: number | null | undefined,
  digits = 3,
  suffix = ""
): string {
  if (isNullOrUndefined(v)) return "not measured";
  const num = typeof v === "number" ? v : parseFloat(String(v));
  if (isNaN(num)) return String(v);
  return `${num.toFixed(digits)}${suffix}`;
}

export function fmtPercent(
  v: number | null | undefined,
  digits = 2
): string {
  if (isNullOrUndefined(v)) return "not measured";
  const num = typeof v === "number" ? v : parseFloat(String(v));
  if (isNaN(num)) return String(v);
  // Check if already in 0..100 or 0..1
  const pct = num <= 1.0 && num >= -1.0 ? num * 100 : num;
  return `${pct.toFixed(digits)}%`;
}

export function fmtInt(v: number | null | undefined): string {
  if (isNullOrUndefined(v)) return "not measured";
  const num = typeof v === "number" ? v : parseInt(String(v), 10);
  if (isNaN(num)) return String(v);
  return num.toLocaleString();
}

export function fmtFloat(v: number | null | undefined, digits = 4): string {
  if (isNullOrUndefined(v)) return "not measured";
  const num = typeof v === "number" ? v : parseFloat(String(v));
  if (isNaN(num)) return String(v);
  return num.toFixed(digits);
}

export function fmtMs(v: number | null | undefined, digits = 2): string {
  if (isNullOrUndefined(v)) return "not measured";
  const num = typeof v === "number" ? v : parseFloat(String(v));
  if (isNaN(num)) return String(v);
  return `${num.toFixed(digits)} ms`;
}

export function fmtSec(v: number | null | undefined, digits = 2): string {
  if (isNullOrUndefined(v)) return "not measured";
  const num = typeof v === "number" ? v : parseFloat(String(v));
  if (isNaN(num)) return String(v);
  return `${num.toFixed(digits)} s`;
}

export function fmtCurrency(
  v: number | null | undefined,
  symbol = "₹"
): string {
  if (isNullOrUndefined(v)) return "not measured";
  const num = typeof v === "number" ? v : parseFloat(String(v));
  if (isNaN(num)) return String(v);
  return `${symbol}${num.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function fmtPValue(v: number | null | undefined): string {
  if (isNullOrUndefined(v)) return "not measured";
  const num = typeof v === "number" ? v : parseFloat(String(v));
  if (isNaN(num)) return String(v);
  if (num < 0.001) return "p < 0.001";
  return `p = ${num.toFixed(3)}`;
}
