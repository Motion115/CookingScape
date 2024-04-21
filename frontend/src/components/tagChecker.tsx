import React, {useState} from "react";
import { Tag } from "antd";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../store";
import { setVideoClip } from "../reducers/playerStateReducer";
import { VideoState } from "../types/InfoTypes";

interface TagCheckerProps {
  videoItems: VideoState[];
}

const TagChecker: React.FC<TagCheckerProps> = (props: TagCheckerProps) => {
  const { videoItems } = props;
  const candidates = ["P1", "P2", "P3"]
  const [tagState, setTagState] = useState([false, false, false]);

  const dispatch = useDispatch<AppDispatch>();

  const handleTagClick = (
    isChecked: boolean,
    id: number
  ) => {
    setTagState((prevState) => {
      const newState = [...prevState];
      newState[id] = isChecked;
      return newState;
    })

    console.log(videoItems[id])
    dispatch(setVideoClip(videoItems[id]))
  };
  return (
    <>
      {candidates.map((candidate, id) => (
        <Tag.CheckableTag key={id} checked={tagState[id]} onChange={(e) => handleTagClick(e, id)}>{candidates[id]}</Tag.CheckableTag>
      ))}
    </>
  );
}

export default TagChecker;
