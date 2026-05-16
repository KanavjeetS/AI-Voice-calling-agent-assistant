import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        app: "#050810",
        sidebar: "#0a0f1e",
        panel: "rgba(255,255,255,0.025)",
        brand: "#4F46E5",
        accent: "#7C3AED",
        good: "#22C55E",
        warn: "#F59E0B",
        danger: "#EF4444"
      },
      fontFamily: {
        heading: ["var(--font-syne)", "system-ui", "sans-serif"],
        body: ["var(--font-dm-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "monospace"]
      }
    }
  },
  plugins: []
};

export default config;
