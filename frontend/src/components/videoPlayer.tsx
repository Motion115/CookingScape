import { Button } from "antd";
import React, { useRef } from "react";
import ReactPlayer from "react-player";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../store";
import { jumpToTime } from "../reducers/jumpToReducer";

const VideoPlayer: React.FC = () => {
  const [duration, setDuration] = React.useState(0);
  const [currentTime, setCurrentTime] = React.useState(0);
  const [timerId, setTimerId] = React.useState<NodeJS.Timeout | null>(null);
  const [isPlay, setIsPlay] = React.useState(false);

  const count = useSelector((state: RootState) => state.jumpTo.time);
  const dispatch = useDispatch<AppDispatch>();

  const playerRef = useRef<ReactPlayer | null>(null);

  const setPlayerRef = (player: ReactPlayer) => {
    playerRef.current = player;
  };

  const durationCallBack = (duration: number) => {
    setDuration(duration);
  };

  const jumpTo = () => {
    let time = 120;
    setCurrentTime(time);

    playerRef.current?.seekTo(time);
    setIsPlay(true);
    // play for duration in the backend and pause
    // Clear the existing timer if it exists
    if (timerId) {
      clearTimeout(timerId);
    }

    // Start a new timer for the specified duration
    const newTimerId = setTimeout(() => {
      setIsPlay(false);
      setTimerId(null);
    }, 5 * 1000); // Convert duration to milliseconds

    setTimerId(newTimerId)
  };

  return (
    <div>
      <ReactPlayer
        style={{ maxWidth: "100%", maxHeight: "100%" }}
        url="./Steak-GR.mp4"
        controls={true}
        onDuration={durationCallBack}
        playing={isPlay}
        ref={setPlayerRef}
      />
      <Button onClick={jumpTo}>test</Button>
      <Button onClick={() => dispatch(jumpToTime())}>increment</Button>
      {count}
    </div>
  );
};

export default VideoPlayer;
