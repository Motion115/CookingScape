import { Button, Flex, Popover, Rate, Space, Typography } from "antd";
import React, { useEffect, useRef } from "react";
import ReactPlayer from "react-player";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../store";
import { VideoState } from "../types/InfoTypes";
import { recordPlayerProgression } from "../reducers/playerTimeReducer";
import { QuestionOutlined } from "@ant-design/icons";
const { Text } = Typography;

interface VideoPlayerProps {
  videoName: string;
}

const VideoPlayer = (props: VideoPlayerProps) => {
  const [timerId, setTimerId] = React.useState<NodeJS.Timeout | null>(null);
  const [isPlay, setIsPlay] = React.useState(false);

  const { videoName } = props;

  const currentClip = useSelector((state: RootState) => state.playerState);
  const dispatch = useDispatch<AppDispatch>();

  const playerRef = useRef<ReactPlayer | null>(null);

  const setPlayerRef = (player: ReactPlayer) => {
    playerRef.current = player;
  };

  const setCurrentTime = () => {
    const currentTime = playerRef.current?.getCurrentTime();
    if (currentTime) {
      dispatch(recordPlayerProgression(currentTime));
    }
  };

  const jumpTo = (currentClipStatus: VideoState) => {
    const { startTime, duration } = currentClipStatus;

    const playAndPause = () => {
      playerRef.current?.seekTo(startTime);
      setIsPlay(true);

      // Clear the existing timer if it exists
      if (timerId) {
        clearTimeout(timerId);
      }

      // Start a new timer for the specified duration
      const newTimerId = setTimeout(() => {
        setIsPlay(false);
        setTimerId(null);
        // playAndPause(); // recursive
      }, duration * 1000); // Convert duration to milliseconds

      setTimerId(newTimerId);
    };

    playAndPause();
  };

  useEffect(() => {
    jumpTo(currentClip);
  }, [currentClip]);

  const configData = useSelector((state: RootState) => state.setData);
  const difficultyRating = configData.difficulty;

  return (
    <div>
      <div style={{ width: "70%", margin: "auto", textAlign: "center", padding: "0 0 10px 0" }}>
        <Flex gap="small" align="center">
          <Text>Difficulty</Text>
          <Rate count={5} value={difficultyRating.rating} />
          <Popover
            content={
              <div style={{ width: "300px", textAlign: "justify" }}>
                <Text>{difficultyRating.reason}</Text>
              </div>
            }
            title="Why this difficulty rating?"
            placement="bottom"
          >
            <Button size="small" type="text">
              Why this difficulty rating
              <QuestionOutlined />
            </Button>
          </Popover>
        </Flex>
      </div>
      <ReactPlayer
        style={{ maxWidth: "100%", maxHeight: "500px", margin: "auto" }}
        url={videoName}
        controls={true}
        playing={isPlay}
        ref={setPlayerRef}
        width={"70%"}
        height={"300px"}
        onPause={setCurrentTime}
        onSeek={setCurrentTime}
      />
    </div>
  );
};

export default VideoPlayer;
