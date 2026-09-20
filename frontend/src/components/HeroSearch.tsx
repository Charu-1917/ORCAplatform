import { useState, type FormEvent } from "react";
import { ArrowRight, Loader2, Waves } from "lucide-react";
import { motion } from "framer-motion";
import PromptSuggestions from "./PromptSuggestions";
import ToggleBar from "./ToggleBar";

interface Props {
  loading: boolean;
  deepReasoning: boolean;
  liveData: boolean;
  voiceMode: boolean;
  onToggle: (key: "deepReasoning" | "liveData" | "voiceMode") => void;
  onSubmit: (query: string) => void;
  compact?: boolean;
}

export default function HeroSearch({
  loading,
  deepReasoning,
  liveData,
  voiceMode,
  onToggle,
  onSubmit,
  compact = false,
}: Props) {
  const [query, setQuery] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!query.trim() || loading) return;
    onSubmit(query.trim());
  }

  return (
    <section className={compact ? "px-4 pb-6 pt-6" : "px-4 pb-10 pt-14 sm:pt-20"}>
      <div className="mx-auto max-w-3xl text-center">
        {!compact && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-5 flex flex-col items-center gap-3"
          >
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-ocean-400 to-ocean-700 shadow-glass-lg">
              <Waves size={26} className="text-white" />
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-ocean-900 sm:text-4xl">
              Ask ORCA about the Indian Ocean
            </h1>
            <p className="max-w-xl text-sm text-ocean-600 sm:text-base">
              Multi-agent marine intelligence for fishermen &amp; coastal communities — powered by
              simulated ISRO satellite data, PFZ reasoning, and multilingual safety advisories.
            </p>
          </motion.div>
        )}

        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="glass-strong flex items-center gap-2 rounded-full p-2 pl-5 shadow-glass-lg"
        >
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Where is the nearest Potential Fishing Zone in Tamil Nadu today?"
            className="min-w-0 flex-1 bg-transparent text-sm text-ocean-900 placeholder:text-ocean-400 focus:outline-none sm:text-[15px]"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-ocean-500 to-ocean-700 text-white shadow-glass transition disabled:cursor-not-allowed disabled:opacity-40 hover:brightness-110"
          >
            {loading ? <Loader2 size={17} className="animate-spin" /> : <ArrowRight size={17} />}
          </button>
        </motion.form>

        <div className="mt-4">
          <ToggleBar
            deepReasoning={deepReasoning}
            liveData={liveData}
            voiceMode={voiceMode}
            onToggle={onToggle}
          />
        </div>

        {!compact && (
          <div className="mt-6">
            <PromptSuggestions onPick={(text) => onSubmit(text)} />
          </div>
        )}
      </div>
    </section>
  );
}
