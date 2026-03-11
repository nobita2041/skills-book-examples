import { Composition } from "remotion";
import { AgentSkillsVideo } from "./AgentSkillsVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="AgentSkillsVideo"
      component={AgentSkillsVideo}
      durationInFrames={900}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
