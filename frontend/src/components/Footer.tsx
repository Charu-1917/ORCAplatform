import WaveBackground from "./WaveBackground";

export default function Footer() {
  return (
    <footer className="wave-scene relative mt-10 bg-ocean-900/95 pt-24 text-ocean-100">
      <div className="absolute inset-x-0 top-0">
        <WaveBackground height={90} flip />
      </div>
      <div className="mx-auto max-w-6xl px-5 pb-8">
        <div className="flex flex-col items-center justify-between gap-4 border-t border-white/10 pt-6 text-center sm:flex-row sm:text-left">
          <p className="text-xs text-ocean-300">
            ORCA — Oceanic Reasoning &amp; Collaborative Agents · Smart India Hackathon Prototype for ISRO ·
            Mock data for demonstration only.
          </p>
          <div className="flex gap-4 text-xs font-medium text-ocean-300">
            <a href="#api-docs" className="hover:text-white">API</a>
            <a href="#docs" className="hover:text-white">Docs</a>
            <a href="https://www.incois.gov.in" target="_blank" rel="noreferrer" className="hover:text-white">
              INCOIS
            </a>
            <a href="https://bhuvan.nrsc.gov.in" target="_blank" rel="noreferrer" className="hover:text-white">
              Bhuvan
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
