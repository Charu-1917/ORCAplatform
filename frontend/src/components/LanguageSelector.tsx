import { useState, useRef, useEffect } from "react";
import { ChevronDown, Languages } from "lucide-react";
import type { LanguageOption } from "../types";

interface Props {
  languages: LanguageOption[];
  value: string;
  onChange: (code: string) => void;
}

export default function LanguageSelector({ languages, value, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const current = languages.find((l) => l.code === value) ?? languages[0];

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 rounded-full glass px-3.5 py-2 text-sm font-medium text-ocean-800 shadow-glass transition hover:shadow-glass-lg"
      >
        <Languages size={15} className="text-ocean-600" />
        <span>{current?.label ?? "English"}</span>
        <ChevronDown size={14} className={`text-ocean-500 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>
      {open && (
        <div className="absolute right-0 z-30 mt-2 w-48 overflow-hidden rounded-2xl glass-strong shadow-glass-lg">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => {
                onChange(lang.code);
                setOpen(false);
              }}
              className={`block w-full px-4 py-2.5 text-left text-sm transition hover:bg-ocean-100/70 ${
                lang.code === value ? "bg-ocean-100/80 font-semibold text-ocean-800" : "text-ocean-700"
              }`}
            >
              {lang.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
