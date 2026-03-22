/** Format seconds as MM:SS */
export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60).toString().padStart(2, "0");
  const s = (seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

/** Convert a 0–1 confidence value to a human-readable label */
export function confidenceLabel(value: number): "high" | "medium" | "low" {
  if (value >= 0.8) return "high";
  if (value >= 0.55) return "medium";
  return "low";
}

/** Generate a short request ID for tracing */
export function generateRequestId(prefix = "req"): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}
