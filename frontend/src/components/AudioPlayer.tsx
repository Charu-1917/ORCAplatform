import { useEffect, useRef, useState } from "react";
import { Play, Pause, Volume2, Square } from "lucide-react";

interface Props {
  text: string;
  languageCode: string;
  languageLabel: string;
  autoPlay?: boolean;
}

const LOCALE_MAP: Record<string, string> = {
  en: "en-IN",
  hi: "hi-IN",
  ta: "ta-IN",
  te: "te-IN",
  ml: "ml-IN",
  bn: "bn-IN",
  gu: "gu-IN",
  mr: "mr-IN",
};

export default function AudioPlayer({ text, languageCode, languageLabel, autoPlay = false }: Props) {
  const [playing, setPlaying] = useState(false);
  const [supported, setSupported] = useState(true);
  const utterRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    setSupported(typeof window !== "undefined" && "speechSynthesis" in window);
    return () => {
      window.speechSynthesis?.cancel();
    };
  }, []);

  useEffect(() => {
    if (autoPlay && supported && text) {
      handlePlay();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text]);

  function handlePlay() {
    if (!supported) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = LOCALE_MAP[languageCode] ?? "en-IN";
    utter.rate = 0.95;
    utter.onend = () => setPlaying(false);
    utter.onerror = () => setPlaying(false);
    utterRef.current = utter;
    window.speechSynthesis.speak(utter);
    setPlaying(true);
  }

  function handlePause() {
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.pause();
      setPlaying(false);
    }
  }

  function handleStop() {
    window.speechSynthesis.cancel();
    setPlaying(false);
  }

  return (
    <div className="flex items-center gap-3 rounded-2xl border border-white/60 bg-white/50 px-4 py-3 shadow-glass">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-ocean-400 to-ocean-600 text-white">
        <Volume2 size={16} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-bold text-ocean-800">Regional Advisory Audio · {languageLabel}</p>
        <p className="truncate text-[11px] text-ocean-500">
          {supported ? "Text-to-speech for local fishermen" : "TTS not supported in this browser"}
        </p>
      </div>
      <div className="flex items-center gap-1.5">
        <button
          onClick={playing ? handlePause : handlePlay}
          disabled={!supported}
          className="flex h-8 w-8 items-center justify-center rounded-full bg-ocean-600 text-white transition hover:brightness-110 disabled:opacity-40"
        >
          {playing ? <Pause size={14} /> : <Play size={14} className="ml-0.5" />}
        </button>
        <button
          onClick={handleStop}
          disabled={!supported}
          className="flex h-8 w-8 items-center justify-center rounded-full bg-white/70 text-ocean-600 shadow-sm transition hover:bg-white disabled:opacity-40"
        >
          <Square size={12} />
        </button>
      </div>
    </div>
  );
}
