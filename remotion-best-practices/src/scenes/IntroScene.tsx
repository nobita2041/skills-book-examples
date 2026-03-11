import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { FONT_FAMILY, COLORS, FONT_SIZES } from "../styles/theme";

export const IntroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleScale = spring({
    frame,
    fps,
    config: { damping: 200 },
  });

  const subtitleProgress = spring({
    frame,
    fps,
    delay: 15,
    config: { damping: 200 },
  });

  const lineWidth = spring({
    frame,
    fps,
    delay: 25,
    config: { damping: 200 },
  });

  const subtitleOpacity = interpolate(subtitleProgress, [0, 1], [0, 1]);
  const subtitleTranslateY = interpolate(subtitleProgress, [0, 1], [30, 0]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 20,
        }}
      >
        <div
          style={{
            fontFamily: FONT_FAMILY,
            fontSize: FONT_SIZES.title,
            fontWeight: "700",
            color: COLORS.textPrimary,
            transform: `scale(${titleScale})`,
            textAlign: "center",
          }}
        >
          Agent Skills の 3つの特徴
        </div>

        <div
          style={{
            width: interpolate(lineWidth, [0, 1], [0, 300]),
            height: 4,
            background: `linear-gradient(90deg, ${COLORS.feature1}, ${COLORS.feature2}, ${COLORS.feature3})`,
            borderRadius: 2,
          }}
        />

        <div
          style={{
            fontFamily: FONT_FAMILY,
            fontSize: FONT_SIZES.featureDesc,
            color: COLORS.textSecondary,
            opacity: subtitleOpacity,
            transform: `translateY(${subtitleTranslateY}px)`,
            marginTop: 10,
          }}
        >
          3 Features of Agent Skills
        </div>
      </div>
    </AbsoluteFill>
  );
};
