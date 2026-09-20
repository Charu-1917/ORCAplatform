/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "Plus Jakarta Sans", "system-ui", "sans-serif"],
      },
      colors: {
        ocean: {
          50: "#F0F6FF",
          100: "#E1ECFD",
          200: "#CADFFB",
          300: "#A9CBF7",
          400: "#7FB0F0",
          500: "#5590E6",
          600: "#3D71C9",
          700: "#325AA0",
          800: "#2C4A7D",
          900: "#1E3253",
        },
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(31, 84, 173, 0.10)",
        "glass-lg": "0 16px 48px 0 rgba(31, 84, 173, 0.16)",
        "glow-green": "0 0 0 4px rgba(34, 197, 94, 0.15)",
        "glow-yellow": "0 0 0 4px rgba(234, 179, 8, 0.15)",
        "glow-red": "0 0 0 4px rgba(239, 68, 68, 0.15)",
      },
      animation: {
        "wave-slow": "wave-move 14s ease-in-out infinite",
        "wave-mid": "wave-move 9s ease-in-out infinite",
        "wave-fast": "wave-move 6s ease-in-out infinite",
        float: "float 6s ease-in-out infinite",
        "pulse-soft": "pulse-soft 2.4s ease-in-out infinite",
        shimmer: "shimmer 2.2s linear infinite",
      },
      keyframes: {
        "wave-move": {
          "0%, 100%": { transform: "translateX(0) translateY(0)" },
          "50%": { transform: "translateX(-2%) translateY(-3px)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" },
        },
        "pulse-soft": {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.55 },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
};
