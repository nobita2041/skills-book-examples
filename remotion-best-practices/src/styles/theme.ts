import { loadFont } from "@remotion/google-fonts/NotoSansJP";

const { fontFamily } = loadFont("normal", {
  weights: ["400", "700"],
});

export const FONT_FAMILY = fontFamily;

export const COLORS = {
  bg: "#0F0F23",
  textPrimary: "#FFFFFF",
  textSecondary: "#A0A0C0",
  feature1: "#00D4FF",
  feature2: "#FF6B6B",
  feature3: "#50FA7B",
  accent: "#BD93F9",
  subtitleBg: "rgba(0, 0, 0, 0.7)",
} as const;

export const FONT_SIZES = {
  title: 64,
  featureNumber: 120,
  featureTitle: 48,
  featureDesc: 28,
  subtitle: 30,
  chartLabel: 20,
  outroItem: 36,
} as const;
