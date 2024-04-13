import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

interface setDataState {
  steps: Object;
  ingredients: Object;
  sceneList: Object;
}

export const initialState: setDataState = {
  steps: {},
  ingredients: {},
  sceneList: {},
};

// load the data async
const setDataSlice = createSlice({
  name: "setData",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(loadDataAsync.fulfilled, (state, action) => {
      state.steps = action.payload.steps;
      state.ingredients = action.payload.ingredients;
      state.sceneList = action.payload.scene_list;
    });
  },
});

export const loadDataAsync = createAsyncThunk(
  "setData/loadDataAsync",
  async (filePath: string) => {
    const response = await fetch(filePath);
    const data = await response.json();
    return data;
  }
);

export default setDataSlice.reducer;
