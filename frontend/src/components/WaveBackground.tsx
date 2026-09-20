interface WaveBackgroundProps {
  height?: number;
  flip?: boolean;
}

const WAVE_SVG =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M0,40 C150,90 350,0 600,40 C850,80 1050,10 1200,40 L1200,120 L0,120 Z' fill='%233D71C9'/%3E%3C/svg%3E";

export default function WaveBackground({ height = 140, flip = false }: WaveBackgroundProps) {
  return (
    <div
      className="wave-scene pointer-events-none w-full"
      style={{ height, transform: flip ? "scaleY(-1)" : undefined }}
      aria-hidden="true"
    >
      <div
        className="wave-layer layer-1"
        style={{ backgroundImage: `url("${WAVE_SVG}")` }}
      />
      <div
        className="wave-layer layer-2"
        style={{ backgroundImage: `url("${WAVE_SVG}")` }}
      />
      <div
        className="wave-layer layer-3"
        style={{ backgroundImage: `url("${WAVE_SVG}")` }}
      />
    </div>
  );
}
