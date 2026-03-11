import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { FONT_FAMILY, COLORS, FONT_SIZES } from "../styles/theme";
import { Subtitle } from "../components/Subtitle";

type FeatureSceneProps = {
  number: string;
  title: string;
  description: string;
  accentColor: string;
  subtitleText: string;
  chart: React.ReactNode;
};

export const FeatureScene: React.FC<FeatureSceneProps> = ({
  number,
  title,
  description,
  accentColor,
  subtitleText,
  chart,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const numberProgress = spring({
    frame,
    fps,
    config: { damping: 200 },
  });

  const titleProgress = spring({
    frame,
    fps,
    delay: 10,
    config: { damping: 200 },
  });

  const descProgress = spring({
    frame,
    fps,
    delay: 20,
    config: { damping: 200 },
  });

  const chartProgress = spring({
    frame,
    fps,
    delay: 15,
    config: { damping: 200 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        padding: 80,
      }}
    >
      <div
        style={{
          display: "flex",
          width: "100%",
          height: "100%",
          gap: 60,
        }}
      >
        {/* Left side: number + title + description */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            gap: 20,
          }}
        >
          <div
            style={{
              fontFamily: FONT_FAMILY,
              fontSize: FONT_SIZES.featureNumber,
              fontWeight: "700",
              color: accentColor,
              opacity: interpolate(numberProgress, [0, 1], [0, 0.3]),
              transform: `scale(${numberProgress})`,
              lineHeight: 1,
            }}
          >
            {number}
          </div>
          <div
            style={{
              fontFamily: FONT_FAMILY,
              fontSize: FONT_SIZES.featureTitle,
              fontWeight: "700",
              color: COLORS.textPrimary,
              opacity: interpolate(titleProgress, [0, 1], [0, 1]),
              transform: `translateX(${interpolate(titleProgress, [0, 1], [40, 0])}px)`,
            }}
          >
            {title}
          </div>
          <div
            style={{
              fontFamily: FONT_FAMILY,
              fontSize: FONT_SIZES.featureDesc,
              color: COLORS.textSecondary,
              opacity: interpolate(descProgress, [0, 1], [0, 1]),
              transform: `translateY(${interpolate(descProgress, [0, 1], [20, 0])}px)`,
              lineHeight: 1.6,
              maxWidth: 500,
            }}
          >
            {description}
          </div>
        </div>

        {/* Right side: chart */}
        <div
          style={{
            flex: 1,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            opacity: interpolate(chartProgress, [0, 1], [0, 1]),
            transform: `scale(${interpolate(chartProgress, [0, 1], [0.8, 1])})`,
          }}
        >
          {chart}
        </div>
      </div>

      <Subtitle text={subtitleText} delay={30} />
    </AbsoluteFill>
  );
};
