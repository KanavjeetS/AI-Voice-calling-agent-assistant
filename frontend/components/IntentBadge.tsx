import clsx from "clsx";

const intentClasses: Record<string, string> = {
  interested: "bg-[#22C55E]/15 text-[#22C55E] border-[#22C55E]/30",
  confused: "bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30",
  angry: "bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30",
  spam_invalid: "bg-[#6B7280]/15 text-[#CBD5E1] border-[#6B7280]/40",
  high_ticket: "bg-[#A78BFA]/15 text-[#A78BFA] border-[#A78BFA]/30",
  callback: "bg-[#3B82F6]/15 text-[#60A5FA] border-[#3B82F6]/30",
  unknown: "bg-slate-500/10 text-slate-300 border-slate-500/20"
};

interface IntentBadgeProps {
  intent: string;
}

export function IntentBadge({ intent }: IntentBadgeProps) {
  return (
    <span className={clsx("inline-flex rounded border px-2 py-1 text-xs font-bold", intentClasses[intent] ?? intentClasses.unknown)}>
      {intent.replace("_", " ")}
    </span>
  );
}
