import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        border: "#E2E8F0",
        input: "#CBD5E1",
        ring: "#2563EB",
        background: "#F8FAFC",
        foreground: "#0F172A",
        primary: {
          DEFAULT: "#2563EB",
          foreground: "#FFFFFF",
          navy: "#1E3A5F",
          hover: "#1D4ED8",
          soft: "#DBEAFE"
        },
        secondary: {
          DEFAULT: "#F1F5F9",
          foreground: "#334155"
        },
        muted: {
          DEFAULT: "#F1F5F9",
          foreground: "#64748B"
        },
        accent: {
          DEFAULT: "#EDE9FE",
          foreground: "#7C3AED",
          violet: "#7C3AED",
          teal: "#0F766E",
          "soft-teal": "#CCFBF1",
          amber: "#D97706",
          "soft-amber": "#FEF3C7"
        },
        success: "#16A34A",
        warning: "#F59E0B",
        danger: "#DC2626",
        card: {
          DEFAULT: "#FFFFFF",
          foreground: "#0F172A"
        },
        popover: {
          DEFAULT: "#FFFFFF",
          foreground: "#0F172A"
        }
      },
      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem",
        sm: "0.25rem"
      },
      boxShadow: {
        card: "0 1px 2px rgb(15 23 42 / 0.06)"
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif"
        ]
      }
    }
  },
  plugins: []
};

export default config;
