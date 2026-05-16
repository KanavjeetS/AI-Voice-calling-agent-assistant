export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(value);
}

export function totalLatency(latency: {
  twilio_ingress_ms: number;
  stt_ms: number;
  llm_ms: number;
  tts_ms: number;
  twilio_egress_ms: number;
}): number {
  return latency.twilio_ingress_ms + latency.stt_ms + latency.llm_ms + latency.tts_ms + latency.twilio_egress_ms;
}
