import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { FONT_FAMILY, COLORS, FONT_SIZES } from "../styles/theme";

const segments = [
  { label: "ルール", value: 35, color: COLORS.feature2 },
  { label: "例示", value: 25, color: COLORS.feature1 },
  { label: "アセット", value: 20, color: COLORS.feature3 },
  { label: "メタデータ", value: 20, color: COLORS.accent },
];

const SIZE = 300;
const CENTER = SIZE / 2;
const RADIUS = 110;
const STROKE_WIDTH = 40;

export const PieChart: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const circumference = 2 * Math.PI * RADIUS;
  const total = segments.reduce((sum, s) => sum + s.value, 0);

  const progress = interpolate(frame, [30, 30 + 3 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  let cumulativeOffset = 0;

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 30 }}>
      <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}>
        {segments.map((segment) => {
          const segmentLength = (segment.value / total) * circumference;
          const currentOffset = cumulativeOffset;
          cumulativeOffset += segmentLength;

          const drawLength = segmentLength * progress;
          const offset = segmentLength - drawLength;

          return (
            <circle
              key={segment.label}
              r={RADIUS}
              cx={CENTER}
              cy={CENTER}
              fill="none"
              stroke={segment.color}
              strokeWidth={STROKE_WIDTH}
              strokeDasharray={`${segmentLength} ${circumference}`}
              strokeDashoffset={offset}
              transform={`rotate(${(currentOffset / circumference) * 360 - 90} ${CENTER} ${CENTER})`}
              strokeLinecap="round"
            />
          );
        })}
      </svg>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {segments.map((segment, i) => {
          const labelOpacity = interpolate(
            frame,
            [40 + i * 10, 55 + i * 10],
            [0, 1],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          );

          return (
            <div
              key={segment.label}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                opacity: labelOpacity,
              }}
            >
              <div
                style={{
                  width: 14,
                  height: 14,
                  borderRadius: 3,
                  backgroundColor: segment.color,
                }}
              />
              <div
                style={{
                  fontFamily: FONT_FAMILY,
                  fontSize: FONT_SIZES.chartLabel,
                  color: COLORS.textPrimary,
                }}
              >
                {segment.label} {segment.value}%
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
