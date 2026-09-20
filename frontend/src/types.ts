export type AlertLevel = "green" | "yellow" | "red";

export interface AgentStep {
  agent: string;
  icon: string;
  status: "pending" | "running" | "done";
  summary: string;
  detail: string;
  duration_ms: number;
}

export interface PFZZone {
  id: string;
  name: string;
  lat: number;
  lng: number;
  radius_km: number;
  score: number;
  depth_m: number;
}

export interface HeatmapPoint {
  lat: number;
  lng: number;
  value: number;
}

export interface CurrentVector {
  lat: number;
  lng: number;
  direction_deg: number;
  speed_kmph: number;
}

export interface Hazard {
  id: string;
  region_name: string;
  title: string;
  level: AlertLevel;
  description: string;
  wind_speed_kmph: number;
  wave_height_m: number;
}

export interface ChartPoint {
  day: string;
  sst: number;
  chlorophyll: number;
}

export interface QueryResponse {
  query: string;
  language: string;
  language_label: string;
  intent: string;
  location_name: string;
  location_state: string;
  center: { lat: number; lng: number };
  alert_level: AlertLevel;
  markdown: string;
  audio_text: string;
  agent_steps: AgentStep[];
  pfz_zones: PFZZone[];
  heatmap: HeatmapPoint[];
  current_vectors: CurrentVector[];
  hazards: Hazard[];
  chart_data: ChartPoint[];
}

export interface LanguageOption {
  code: string;
  label: string;
}

export interface LocationOption {
  key: string;
  name: string;
  state: string;
  lat: number;
  lng: number;
}
