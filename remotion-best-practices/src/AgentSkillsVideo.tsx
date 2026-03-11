import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { fade } from "@remotion/transitions/fade";
import { COLORS } from "./styles/theme";
import { IntroScene } from "./scenes/IntroScene";
import { FeatureScene } from "./scenes/FeatureScene";
import { OutroScene } from "./scenes/OutroScene";
import { BarChart } from "./charts/BarChart";
import { PieChart } from "./charts/PieChart";
import { NetworkChart } from "./charts/NetworkChart";

const TRANSITION_DURATION = 15;

export const AgentSkillsVideo: React.FC = () => {
  return (
    <TransitionSeries>
      {/* Intro: 105f = 3.5s */}
      <TransitionSeries.Sequence durationInFrames={105}>
        <IntroScene />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
      />

      {/* Feature 1: 段階的開示 - 255f = 8.5s */}
      <TransitionSeries.Sequence durationInFrames={255}>
        <FeatureScene
          number="01"
          title="段階的開示"
          description="スキルが必要に応じて複雑さを段階的に明かし、エージェントの認知負荷を最小化します。"
          accentColor={COLORS.feature1}
          subtitleText="Progressive Disclosure - スキルが複雑さを段階的に明かす"
          chart={<BarChart />}
        />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
      />

      {/* Feature 2: ドメイン知識のパッケージ化 - 255f = 8.5s */}
      <TransitionSeries.Sequence durationInFrames={255}>
        <FeatureScene
          number="02"
          title="ドメイン知識のパッケージ化"
          description="専門的なドメイン知識をスキルとしてパッケージ化し、再利用可能な形で提供します。"
          accentColor={COLORS.feature2}
          subtitleText="Domain Knowledge Packaging - ドメイン知識を再利用可能に"
          chart={<PieChart />}
        />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
      />

      {/* Feature 3: 相互運用性 - 255f = 8.5s */}
      <TransitionSeries.Sequence durationInFrames={255}>
        <FeatureScene
          number="03"
          title="相互運用性"
          description="異なるエージェント間でスキルを共有し、エコシステム全体の能力を高めます。"
          accentColor={COLORS.feature3}
          subtitleText="Interoperability - エージェント間でスキルを共有"
          chart={<NetworkChart />}
        />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
      />

      {/* Outro: 90f = 3.0s */}
      <TransitionSeries.Sequence durationInFrames={90}>
        <OutroScene />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
