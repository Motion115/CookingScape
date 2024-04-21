import { createSlice } from "@reduxjs/toolkit";
import { VideoState } from "../types/InfoTypes";

const initialState: VideoState = {
  startTime: 0,
  duration: 0,
};

const playerStateSlice = createSlice({
  name: "playerState",
  initialState,
  reducers: {
    setVideoClip(state, action) {
      // console.log(action.payload);
      state.startTime = action.payload.startTime;
      state.duration = action.payload.duration;
    },
  },
});

export const { setVideoClip } = playerStateSlice.actions;

export default playerStateSlice.reducer;
