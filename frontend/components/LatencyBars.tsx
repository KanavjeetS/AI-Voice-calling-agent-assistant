import type { LatencyBreakdown } from "@/types/api";

interface LatencyBarsProps {
  latency: LatencyBreakdown;
}

type LatencyKey = "twilio_ingress_ms" | "stt_ms" | "llm_ms" | "tts_ms" | "twilio_egress_ms";

const stages: Array<{ key: LatencyKey; label: string; color: string }> = [
  { key: "twilio_ingress_ms", label: "Twilio in", color: "bg-sky-400" },
  { key: "stt_ms", label: "STT", color: "bg-emerald-400" },
  { key: "llm_ms", label: "LLM", color: "bg-indigo-400" },
  { key: "tts_ms", label: "TTS", color: "bg-amber-400" },
  { key: "twilio_egress_ms", label: "Twilio out", color: "bg-rose-400" }
];

export function LatencyBars({ latency }: LatencyBarsProps) {
  return (
    <div className="space-y-2">
      {stages.map((stage) => (
        <div key={stage.key} className="grid grid-cols-[88px_1fr_64px] items-center gap-3 text-xs">
          <span className="text-slate-400">{stage.label}</span>
          <div className="h-2 rounded-full bg-white/10">
            <div className={`${stage.color} h-full rounded-full`} />
          </div>
          <span className="text-right font-mono text-slate-300">{latency[stage.key]}ms</span>
        </div>
      ))}
    </div>
  );
}
