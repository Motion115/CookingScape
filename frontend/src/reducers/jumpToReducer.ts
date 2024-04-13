import { createSlice } from "@reduxjs/toolkit";

interface JumpToState {
  time: number;
  duration: number;
}

const initialState: JumpToState = {
  time: 0,
  duration: 0,
}

const jumpToSlice = createSlice({
  name: 'jumpTo',
  initialState,
  reducers: {
    jumpToTime: (state) => {
      state.time += 1;
    }
  },
})

export const {jumpToTime} = jumpToSlice.actions;

export default jumpToSlice.reducer;