import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import type { ChartPoint } from "../types";

interface Props {
  data: ChartPoint[];
}

export default function ChartPanel({ data }: Props) {
  return (
    <div className="h-64 w-full rounded-2xl border border-white/60 bg-white/40 p-3 shadow-glass sm:h-72">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 16, bottom: 0, left: -12 }}>
          <defs>
            <linearGradient id="sstGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#5590E6" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#5590E6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#CADFFB" />
          <XAxis dataKey="day" tick={{ fontSize: 11, fill: "#5A6B85" }} />
          <YAxis
            yAxisId="sst"
            tick={{ fontSize: 11, fill: "#5A6B85" }}
            domain={["auto", "auto"]}
            label={{ value: "SST °C", angle: -90, position: "insideLeft", fontSize: 10, fill: "#5A6B85" }}
          />
          <YAxis
            yAxisId="chl"
            orientation="right"
            tick={{ fontSize: 11, fill: "#5A6B85" }}
            domain={["auto", "auto"]}
            label={{ value: "Chl-a mg/m³", angle: 90, position: "insideRight", fontSize: 10, fill: "#5A6B85" }}
          />
          <Tooltip
            contentStyle={{
              borderRadius: 12,
              border: "1px solid #CADFFB",
              fontSize: 12,
              background: "rgba(255,255,255,0.95)",
            }}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Area
            yAxisId="sst"
            type="monotone"
            dataKey="sst"
            name="SST (°C)"
            stroke="#3D71C9"
            fill="url(#sstGradient)"
            strokeWidth={2}
          />
          <Line
            yAxisId="chl"
            type="monotone"
            dataKey="chlorophyll"
            name="Chlorophyll-a (mg/m³)"
            stroke="#22c55e"
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
