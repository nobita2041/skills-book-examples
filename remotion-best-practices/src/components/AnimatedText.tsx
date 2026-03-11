import { spring, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { FONT_FAMILY, COLORS } from "../styles/theme";

type AnimatedTextProps = {
  text: string;
  fontSize: number;
  color?: string;
  fontWeight?: string;
  delay?: number;
  direction?: "up" | "left";
};

export const AnimatedText: React.FC<AnimatedTextProps> = ({
  text,
  fontSize,
  color = COLORS.textPrimary,
  fontWeight = "400",
  delay = 0,
  direction = "up",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame,
    fps,
    delay,
    config: { damping: 200 },
  });

  const opacity = interpolate(progress, [0, 1], [0, 1]);
  const translateY = direction === "up" ? interpolate(progress, [0, 1], [40, 0]) : 0;
  const translateX = direction === "left" ? interpolate(progress, [0, 1], [60, 0]) : 0;

  return (
    <div
      style={{
        fontFamily: FONT_FAMILY,
        fontSize,
        fontWeight,
        color,
        opacity,
        transform: `translate(${translateX}px, ${translateY}px)`,
      }}
    >
      {text}
    </div>
  );
};
