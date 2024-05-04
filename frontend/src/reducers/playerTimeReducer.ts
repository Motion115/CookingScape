import { createSlice } from "@reduxjs/toolkit";
import { VideoTime } from "../types/InfoTypes";

const initialState: VideoTime = {
  time: 0,
};

const playerStateSlice = createSlice({
  name: "playerTime",
  initialState,
  reducers: {
    recordPlayerProgression(state, action) {
      state.time = action.payload;
    },
  },
});

export const { recordPlayerProgression } = playerStateSlice.actions;

export default playerStateSlice.reducer;
