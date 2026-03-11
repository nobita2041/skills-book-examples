import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FONT_FAMILY, COLORS, FONT_SIZES } from "../styles/theme";

const STAGGER_DELAY = 8;

const data = [
  { label: "Level 1", value: 0.2 },
  { label: "Level 2", value: 0.4 },
  { label: "Level 3", value: 0.6 },
  { label: "Level 4", value: 0.8 },
  { label: "Level 5", value: 1.0 },
];

const BAR_WIDTH = 60;
const CHART_HEIGHT = 350;
const GAP = 20;

export const BarChart: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div
      style={{
        display: "flex",
        alignItems: "flex-end",
        gap: GAP,
        height: CHART_HEIGHT,
      }}
    >
      {data.map((item, i) => {
        const height = spring({
          frame,
          fps,
          delay: 30 + i * STAGGER_DELAY,
          config: { damping: 200 },
        });

        const barHeight = height * item.value * CHART_HEIGHT;

        return (
          <div
            key={item.label}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 8,
            }}
          >
            <div
              style={{
                width: BAR_WIDTH,
                height: barHeight,
                background: `linear-gradient(180deg, ${COLORS.feature1}, ${COLORS.feature1}88)`,
                borderRadius: 6,
              }}
            />
            <div
              style={{
                fontFamily: FONT_FAMILY,
                fontSize: FONT_SIZES.chartLabel,
                color: COLORS.textSecondary,
              }}
            >
              {item.label}
            </div>
          </div>
        );
      })}
    </div>
  );
};
