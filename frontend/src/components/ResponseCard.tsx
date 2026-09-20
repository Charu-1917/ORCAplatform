import { motion } from "framer-motion";
import { MapPin, AlertTriangle, ShieldCheck, ShieldAlert } from "lucide-react";
import clsx from "clsx";
import type { QueryResponse } from "../types";
import { SimpleMarkdown } from "../lib/markdown";
import AgentWorkflowVisualizer from "./AgentWorkflowVisualizer";
import MapView from "./MapView";
import ChartPanel from "./ChartPanel";
import AudioPlayer from "./AudioPlayer";

interface Props {
  response: QueryResponse;
  voiceMode: boolean;
}

const ALERT_STYLES = {
  green: {
    label: "SAFE",
    icon: ShieldCheck,
    className: "bg-emerald-50 text-emerald-700 border-emerald-200",
  },
  yellow: {
    label: "CAUTION",
    icon: AlertTriangle,
    className: "bg-amber-50 text-amber-700 border-amber-200",
  },
  red: {
    label: "DANGER",
    icon: ShieldAlert,
    className: "bg-red-50 text-red-700 border-red-200",
  },
} as const;

export default function ResponseCard({ response, voiceMode }: Props) {
  const alertStyle = ALERT_STYLES[response.alert_level];
  const AlertIcon = alertStyle.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mx-auto max-w-4xl space-y-4 px-4 pb-16"
    >
      {/* Query recap header */}
      <div className="glass rounded-2xl px-5 py-4 shadow-glass">
        <p className="text-[11px] font-semibold uppercase tracking-wide text-ocean-400">You asked</p>
        <p className="mt-0.5 text-sm font-medium text-ocean-900 sm:text-base">"{response.query}"</p>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="flex items-center gap-1.5 rounded-full bg-ocean-100/80 px-3 py-1 text-xs font-semibold text-ocean-700">
            <MapPin size={12} />
            {response.location_name}, {response.location_state}
          </span>
          <span
            className={clsx(
              "flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold",
              alertStyle.className
            )}
          >
            <AlertIcon size={12} />
            {alertStyle.label}
          </span>
          <span className="rounded-full bg-ocean-100/80 px-3 py-1 text-xs font-semibold text-ocean-700">
            {response.language_label}
          </span>
        </div>
      </div>

      {/* Agent workflow visualizer / chain-of-thought */}
      <AgentWorkflowVisualizer steps={response.agent_steps} />

      {/* Markdown advisory */}
      <div className="glass rounded-2xl px-5 py-5 shadow-glass">
        <SimpleMarkdown text={response.markdown} />
      </div>

      {/* Audio widget */}
      <AudioPlayer
        text={response.audio_text}
        languageCode={response.language}
        languageLabel={response.language_label}
        autoPlay={voiceMode}
      />

      {/* Map */}
      <div>
        <p className="mb-2 text-xs font-bold uppercase tracking-wide text-ocean-500">
          PFZ &amp; SST Map — {response.location_name}
        </p>
        <MapView
          center={response.center}
          pfzZones={response.pfz_zones}
          heatmap={response.heatmap}
          alertLevel={response.alert_level}
        />
      </div>

      {/* Chart */}
      <div>
        <p className="mb-2 text-xs font-bold uppercase tracking-wide text-ocean-500">
          Sea Surface Temp vs Chlorophyll-a (7 days)
        </p>
        <ChartPanel data={response.chart_data} />
      </div>
    </motion.div>
  );
}
