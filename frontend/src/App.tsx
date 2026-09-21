import { useEffect, useState } from "react";
import { AlertCircle } from "lucide-react";
import Header from "./components/Header";
import HeroSearch from "./components/HeroSearch";
import ResponseCard from "./components/ResponseCard";
import Footer from "./components/Footer";
import WaveBackground from "./components/WaveBackground";
import { fetchLanguages, runQuery } from "./api";
import type { LanguageOption, QueryResponse } from "./types";

const FALLBACK_LANGUAGES: LanguageOption[] = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "ta", label: "Tamil" },
  { code: "te", label: "Telugu" },
  { code: "ml", label: "Malayalam" },
  { code: "bn", label: "Bengali" },
  { code: "gu", label: "Gujarati" },
  { code: "mr", label: "Marathi" },
];

const SCRIPT_LANGUAGE_RANGES: Record<string, [number, number]> = {
  hi: [0x0900, 0x097f],
  bn: [0x0980, 0x09ff],
  gu: [0x0a80, 0x0aff],
  ta: [0x0b80, 0x0bff],
  te: [0x0c00, 0x0c7f],
  ml: [0x0d00, 0x0d7f],
};

function detectQueryLanguage(query: string): string | null {
  for (const [code, [start, end]] of Object.entries(SCRIPT_LANGUAGE_RANGES)) {
    if ([...query].some((character) => {
      const value = character.codePointAt(0) ?? 0;
      return value >= start && value <= end;
    })) {
      return code;
    }
  }
  return null;
}

export default function App() {
  const [languages, setLanguages] = useState<LanguageOption[]>(FALLBACK_LANGUAGES);
  const [language, setLanguage] = useState("en");
  const [deepReasoning, setDeepReasoning] = useState(true);
  const [liveData, setLiveData] = useState(false);
  const [voiceMode, setVoiceMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<QueryResponse | null>(null);

  useEffect(() => {
    fetchLanguages()
      .then((langs) => langs.length && setLanguages(langs))
      .catch(() => {
        /* fall back to static list if backend isn't reachable yet */
      });
  }, []);

  function handleToggle(key: "deepReasoning" | "liveData" | "voiceMode") {
    if (key === "deepReasoning") setDeepReasoning((v) => !v);
    if (key === "liveData") setLiveData((v) => !v);
    if (key === "voiceMode") setVoiceMode((v) => !v);
  }

  async function handleSubmit(query: string) {
    setLoading(true);
    setError(null);
    try {
      const queryLanguage = detectQueryLanguage(query);
      const result = await runQuery({
        query,
        language: queryLanguage ?? language,
        deep_reasoning: deepReasoning,
        live_data: liveData,
        voice_mode: voiceMode,
      });
      setResponse(result);
      setLanguage(result.language);
    } catch (e) {
      console.error(e);
      setError(
        "Couldn't reach the ORCA backend. Make sure the FastAPI server is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative flex min-h-screen flex-col">
      <Header languages={languages} language={language} onLanguageChange={setLanguage} />

      <main className="relative flex-1">
        {!response && (
          <div className="pointer-events-none absolute inset-x-0 top-24 -z-10 opacity-60">
            <WaveBackground height={220} />
          </div>
        )}

        <HeroSearch
          loading={loading}
          deepReasoning={deepReasoning}
          liveData={liveData}
          voiceMode={voiceMode}
          onToggle={handleToggle}
          onSubmit={handleSubmit}
          compact={!!response}
        />

        {error && (
          <div className="mx-auto mb-6 flex max-w-xl items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        {loading && !response && (
          <div className="mx-auto max-w-3xl px-4 pb-10 text-center text-sm text-ocean-500">
            ORCA agents are analyzing satellite &amp; ocean data…
          </div>
        )}

        {response && <ResponseCard response={response} voiceMode={voiceMode} />}
      </main>

      <Footer />
    </div>
  );
}
