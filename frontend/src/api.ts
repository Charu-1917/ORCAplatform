import axios from "axios";
import type { LanguageOption, LocationOption, QueryResponse } from "./types";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/",
  timeout: 20000,
});

export interface QueryPayload {
  query: string;
  language?: string | null;
  deep_reasoning: boolean;
  live_data: boolean;
  voice_mode: boolean;
}

export async function runQuery(payload: QueryPayload): Promise<QueryResponse> {
  const { data } = await client.post<QueryResponse>("/api/query", payload);
  return data;
}

export async function fetchLanguages(): Promise<LanguageOption[]> {
  const { data } = await client.get<LanguageOption[]>("/api/languages");
  return data;
}

export async function fetchLocations(): Promise<LocationOption[]> {
  const { data } = await client.get<LocationOption[]>("/api/locations");
  return data;
}
