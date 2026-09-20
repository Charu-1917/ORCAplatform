import { Sparkles } from "lucide-react";

const SUGGESTIONS = [
  "Where is the nearest Potential Fishing Zone (PFZ) in Tamil Nadu today?",
  "Check cyclone and high wave advisories near Gujarat coast",
  "Analyze SST and Chlorophyll correlation off Kochi",
  "Is it safe to go fishing near Visakhapatnam this week?",
  "Show potential fishing zones near Kanyakumari in Tamil",
];

interface Props {
  onPick: (text: string) => void;
}

export default function PromptSuggestions({ onPick }: Props) {
  return (
    <div className="flex flex-wrap items-center justify-center gap-2 px-2">
      {SUGGESTIONS.map((s) => (
        <button
          key={s}
          onClick={() => onPick(s)}
          className="group flex items-center gap-1.5 rounded-full glass px-3.5 py-2 text-xs font-medium text-ocean-700 shadow-glass transition hover:-translate-y-0.5 hover:shadow-glass-lg hover:text-ocean-900"
        >
          <Sparkles size={12} className="text-ocean-400 transition group-hover:text-ocean-600" />
          {s}
        </button>
      ))}
    </div>
  );
}
