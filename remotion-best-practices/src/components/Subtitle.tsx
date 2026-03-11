import { spring, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { FONT_FAMILY, COLORS, FONT_SIZES } from "../styles/theme";

type SubtitleProps = {
  text: string;
  delay?: number;
};

export const Subtitle: React.FC<SubtitleProps> = ({ text, delay = 15 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame,
    fps,
    delay,
    config: { damping: 200 },
  });

  const opacity = interpolate(progress, [0, 1], [0, 1]);
  const translateY = interpolate(progress, [0, 1], [20, 0]);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 60,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        opacity,
        transform: `translateY(${translateY}px)`,
      }}
    >
      <div
        style={{
          background: COLORS.subtitleBg,
          backdropFilter: "blur(10px)",
          padding: "12px 40px",
          borderRadius: 30,
          fontFamily: FONT_FAMILY,
          fontSize: FONT_SIZES.subtitle,
          color: COLORS.textPrimary,
          letterSpacing: 1,
        }}
      >
        {text}
      </div>
    </div>
  );
};
