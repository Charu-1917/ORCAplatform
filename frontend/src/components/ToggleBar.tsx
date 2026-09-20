import type { ReactNode } from "react";
import { BrainCircuit, SatelliteDish, Mic } from "lucide-react";
import clsx from "clsx";

interface Props {
  deepReasoning: boolean;
  liveData: boolean;
  voiceMode: boolean;
  onToggle: (key: "deepReasoning" | "liveData" | "voiceMode") => void;
}

export default function ToggleBar({ deepReasoning, liveData, voiceMode, onToggle }: Props) {
  const items: { key: "deepReasoning" | "liveData" | "voiceMode"; label: string; icon: ReactNode; active: boolean }[] = [
    {
      key: "deepReasoning",
      label: "DeepReasoning (Agentic)",
      icon: <BrainCircuit size={14} />,
      active: deepReasoning,
    },
    {
      key: "liveData",
      label: "Live ISRO Earth Data",
      icon: <SatelliteDish size={14} />,
      active: liveData,
    },
    {
      key: "voiceMode",
      label: "Voice Mode",
      icon: <Mic size={14} />,
      active: voiceMode,
    },
  ];

  return (
    <div className="flex flex-wrap items-center justify-center gap-2">
      {items.map((item) => (
        <button
          key={item.key}
          onClick={() => onToggle(item.key)}
          className={clsx(
            "flex items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-xs font-semibold transition",
            item.active
              ? "pill-toggle-active border-transparent"
              : "border-ocean-200/80 bg-white/50 text-ocean-600 hover:bg-white/80"
          )}
        >
          {item.icon}
          {item.label}
        </button>
      ))}
    </div>
  );
}
