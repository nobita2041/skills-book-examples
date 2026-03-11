import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { FONT_FAMILY, COLORS, FONT_SIZES } from "../styles/theme";

const features = [
  { label: "段階的開示", color: COLORS.feature1 },
  { label: "ドメイン知識のパッケージ化", color: COLORS.feature2 },
  { label: "相互運用性", color: COLORS.feature3 },
];

export const OutroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const titleProgress = spring({
    frame,
    fps,
    config: { damping: 200 },
  });

  const fadeOut = interpolate(
    frame,
    [durationInFrames - 30, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        justifyContent: "center",
        alignItems: "center",
        opacity: fadeOut,
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 40,
        }}
      >
        <div
          style={{
            fontFamily: FONT_FAMILY,
            fontSize: FONT_SIZES.featureTitle,
            fontWeight: "700",
            color: COLORS.textPrimary,
            opacity: interpolate(titleProgress, [0, 1], [0, 1]),
            transform: `scale(${titleProgress})`,
          }}
        >
          Agent Skills
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 24,
          }}
        >
          {features.map((feature, i) => {
            const itemProgress = spring({
              frame,
              fps,
              delay: 10 + i * 8,
              config: { damping: 200 },
            });

            return (
              <div
                key={feature.label}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 20,
                  opacity: interpolate(itemProgress, [0, 1], [0, 1]),
                  transform: `translateX(${interpolate(itemProgress, [0, 1], [50, 0])}px)`,
                }}
              >
                <div
                  style={{
                    width: 16,
                    height: 16,
                    borderRadius: 8,
                    backgroundColor: feature.color,
                  }}
                />
                <div
                  style={{
                    fontFamily: FONT_FAMILY,
                    fontSize: FONT_SIZES.outroItem,
                    color: COLORS.textPrimary,
                  }}
                >
                  {feature.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
