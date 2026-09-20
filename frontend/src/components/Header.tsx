import { Waves, BookOpen, Code2 } from "lucide-react";
import LanguageSelector from "./LanguageSelector";
import type { LanguageOption } from "../types";

interface Props {
  languages: LanguageOption[];
  language: string;
  onLanguageChange: (code: string) => void;
}

export default function Header({ languages, language, onLanguageChange }: Props) {
  return (
    <header className="sticky top-0 z-40 border-b border-white/40 bg-white/40 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-3.5">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-ocean-400 to-ocean-700 shadow-glass">
            <Waves size={18} className="text-white" />
          </div>
          <div className="leading-tight">
            <p className="text-[15px] font-extrabold tracking-tight text-ocean-900">ORCA</p>
            <p className="text-[10px] font-medium uppercase tracking-wider text-ocean-500">
              Oceanic Reasoning &amp; Collaborative Agents
            </p>
          </div>
          <span className="ml-2 hidden rounded-full border border-ocean-200 bg-ocean-50/80 px-2.5 py-1 text-[10px] font-semibold text-ocean-600 sm:inline-block">
            ISRO · SIH Prototype
          </span>
        </div>

        <nav className="flex items-center gap-2.5">
          <a
            href="#api-docs"
            className="hidden items-center gap-1.5 rounded-full px-3.5 py-2 text-sm font-medium text-ocean-700 transition hover:bg-white/60 sm:flex"
          >
            <Code2 size={15} />
            API
          </a>
          <a
            href="#docs"
            className="hidden items-center gap-1.5 rounded-full px-3.5 py-2 text-sm font-medium text-ocean-700 transition hover:bg-white/60 sm:flex"
          >
            <BookOpen size={15} />
            Docs
          </a>
          <LanguageSelector languages={languages} value={language} onChange={onLanguageChange} />
        </nav>
      </div>
    </header>
  );
}
