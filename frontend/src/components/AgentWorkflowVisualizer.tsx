import { useState, type ComponentType } from "react";
import {
  BrainCircuit,
  Satellite,
  Waves,
  ShieldAlert,
  Sparkles,
  ChevronDown,
  CheckCircle2,
  ListTree,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { AgentStep } from "../types";
import { renderInline } from "../lib/markdown";

const ICONS: Record<string, ComponentType<{ size?: number; className?: string }>> = {
  brain: BrainCircuit,
  satellite: Satellite,
  waves: Waves,
  "shield-alert": ShieldAlert,
  sparkles: Sparkles,
};

interface Props {
  steps: AgentStep[];
}

export default function AgentWorkflowVisualizer({ steps }: Props) {
  const [expanded, setExpanded] = useState(true);
  const [openStep, setOpenStep] = useState<number | null>(null);

  const totalMs = steps.reduce((sum, s) => sum + s.duration_ms, 0);

  return (
    <div className="glass overflow-hidden rounded-2xl shadow-glass">
      <button
        onClick={() => setExpanded((e) => !e)}
        className="flex w-full items-center justify-between px-4 py-3.5"
      >
        <div className="flex items-center gap-2 text-sm font-semibold text-ocean-800">
          <ListTree size={16} className="text-ocean-500" />
          Agent Workflow Visualizer
          <span className="rounded-full bg-ocean-100/80 px-2 py-0.5 text-[10px] font-bold text-ocean-600">
            {steps.length} agents · {totalMs}ms
          </span>
        </div>
        <ChevronDown
          size={16}
          className={`text-ocean-500 transition-transform ${expanded ? "rotate-180" : ""}`}
        />
      </button>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="space-y-2 px-4 pb-4">
              {steps.map((step, i) => {
                const Icon = ICONS[step.icon] ?? Sparkles;
                const isOpen = openStep === i;
                return (
                  <motion.div
                    key={step.agent}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}
                    className="rounded-xl border border-white/60 bg-white/50 transition"
                  >
                    <button
                      className="flex w-full items-center gap-3 px-3.5 py-2.5 text-left"
                      onClick={() => setOpenStep(isOpen ? null : i)}
                    >
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-ocean-100 to-ocean-200 text-ocean-700">
                        <Icon size={15} />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-xs font-bold text-ocean-800">{step.agent}</p>
                        <p className="truncate text-[11px] text-ocean-500">{step.summary}</p>
                      </div>
                      <span className="flex items-center gap-1 text-[10px] font-semibold text-emerald-600">
                        <CheckCircle2 size={13} />
                        {step.duration_ms}ms
                      </span>
                      <ChevronDown
                        size={13}
                        className={`shrink-0 text-ocean-400 transition-transform ${isOpen ? "rotate-180" : ""}`}
                      />
                    </button>
                    <AnimatePresence initial={false}>
                      {isOpen && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2 }}
                          className="overflow-hidden"
                        >
                          <div className="space-y-1.5 border-t border-white/60 px-4 py-3 text-[12px] leading-relaxed text-ocean-700">
                            {step.detail.split("\n\n").map((line, li) => (
                              <p key={li}>{renderInline(line, li)}</p>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
