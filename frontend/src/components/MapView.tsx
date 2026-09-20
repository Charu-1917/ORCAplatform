import { MapContainer, TileLayer, Circle, CircleMarker, Popup, Tooltip } from "react-leaflet";
import type { AlertLevel, HeatmapPoint, PFZZone } from "../types";

interface Props {
  center: { lat: number; lng: number };
  pfzZones: PFZZone[];
  heatmap: HeatmapPoint[];
  alertLevel: AlertLevel;
}

const ALERT_COLORS: Record<AlertLevel, string> = {
  green: "#22c55e",
  yellow: "#eab308",
  red: "#ef4444",
};

function sstColor(value: number): string {
  if (value < 26.5) return "#60a5fa";
  if (value < 27.5) return "#34d399";
  if (value < 28.5) return "#fbbf24";
  return "#f87171";
}

export default function MapView({ center, pfzZones, heatmap, alertLevel }: Props) {
  const position: [number, number] = [center.lat, center.lng];

  return (
    <div className="h-[380px] w-full overflow-hidden rounded-2xl border border-white/60 shadow-glass sm:h-[440px]">
      <MapContainer center={position} zoom={9} scrollWheelZoom={false} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Safety boundary ring */}
        <Circle
          center={position}
          radius={45000}
          pathOptions={{
            color: ALERT_COLORS[alertLevel],
            fillOpacity: 0.04,
            weight: 2,
            dashArray: "6 6",
          }}
        >
          <Tooltip direction="top" opacity={0.9}>
            Safety boundary — {alertLevel.toUpperCase()} zone
          </Tooltip>
        </Circle>

        {/* SST heatmap grid */}
        {heatmap.map((pt, i) => (
          <CircleMarker
            key={i}
            center={[pt.lat, pt.lng]}
            radius={11}
            pathOptions={{ color: sstColor(pt.value), fillColor: sstColor(pt.value), fillOpacity: 0.35, weight: 0 }}
          >
            <Tooltip direction="top" opacity={0.9}>
              SST {pt.value.toFixed(1)} °C
            </Tooltip>
          </CircleMarker>
        ))}

        {/* PFZ zones */}
        {pfzZones.map((zone) => (
          <Circle
            key={zone.id}
            center={[zone.lat, zone.lng]}
            radius={zone.radius_km * 1000}
            pathOptions={{ color: "#3D71C9", fillColor: "#5590E6", fillOpacity: 0.28, weight: 2 }}
          >
            <Popup>
              <div className="text-xs">
                <p className="font-bold">{zone.name}</p>
                <p>Score: {zone.score.toFixed(2)}</p>
                <p>Depth: {zone.depth_m} m</p>
                <p>Radius: {zone.radius_km} km</p>
              </div>
            </Popup>
          </Circle>
        ))}
      </MapContainer>
    </div>
  );
}
