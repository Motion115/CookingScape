import React from "react";
import ReactPlayer from "react-player";

const VideoPlayer: React.FC = () => {
  return (
    <div>
      <ReactPlayer url="https://www.youtube.com/watch?v=LXb3EKWsInQ" />
    </div>
  );
};

export default VideoPlayer;
