import { useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { evolvePath } from "@remotion/paths";
import { FONT_FAMILY, COLORS, FONT_SIZES } from "../styles/theme";

const SIZE = 400;
const CENTER_X = SIZE / 2;
const CENTER_Y = SIZE / 2;
const OUTER_RADIUS = 140;

const centerNode = { x: CENTER_X, y: CENTER_Y, label: "Skill", color: COLORS.feature3 };

const outerNodes = [
  { x: CENTER_X, y: CENTER_Y - OUTER_RADIUS, label: "Agent A", color: COLORS.feature1 },
  { x: CENTER_X + OUTER_RADIUS, y: CENTER_Y, label: "Agent B", color: COLORS.feature2 },
  { x: CENTER_X, y: CENTER_Y + OUTER_RADIUS, label: "Agent C", color: COLORS.accent },
  { x: CENTER_X - OUTER_RADIUS, y: CENTER_Y, label: "Agent D", color: COLORS.feature1 },
];

type Edge = { from: { x: number; y: number }; to: { x: number; y: number } };

const edges: Edge[] = [
  ...outerNodes.map((n) => ({ from: centerNode, to: n })),
  { from: outerNodes[0]!, to: outerNodes[1]! },
  { from: outerNodes[2]!, to: outerNodes[3]! },
];

const NODE_RADIUS = 30;

export const NetworkChart: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const nodeOpacity = interpolate(frame, [20, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}>
      {/* Edges */}
      {edges.map((edge, i) => {
        const path = `M ${edge.from.x} ${edge.from.y} L ${edge.to.x} ${edge.to.y}`;
        const edgeProgress = interpolate(
          frame,
          [30 + i * 8, 30 + i * 8 + 2 * fps],
          [0, 1],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.quad),
          },
        );
        const { strokeDasharray, strokeDashoffset } = evolvePath(edgeProgress, path);

        return (
          <path
            key={i}
            d={path}
            fill="none"
            stroke={COLORS.textSecondary}
            strokeWidth={2}
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            opacity={0.5}
          />
        );
      })}

      {/* Center node */}
      <circle
        cx={centerNode.x}
        cy={centerNode.y}
        r={NODE_RADIUS + 5}
        fill={centerNode.color}
        opacity={nodeOpacity}
      />
      <text
        x={centerNode.x}
        y={centerNode.y + 6}
        textAnchor="middle"
        fontFamily={FONT_FAMILY}
        fontSize={FONT_SIZES.chartLabel}
        fontWeight="700"
        fill={COLORS.bg}
        opacity={nodeOpacity}
      >
        {centerNode.label}
      </text>

      {/* Outer nodes */}
      {outerNodes.map((node, i) => {
        const itemOpacity = interpolate(
          frame,
          [25 + i * 6, 40 + i * 6],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        );

        return (
          <g key={node.label} opacity={itemOpacity}>
            <circle cx={node.x} cy={node.y} r={NODE_RADIUS} fill={node.color} />
            <text
              x={node.x}
              y={node.y + 6}
              textAnchor="middle"
              fontFamily={FONT_FAMILY}
              fontSize={16}
              fontWeight="700"
              fill={COLORS.bg}
            >
              {node.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};
