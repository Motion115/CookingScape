import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { CookingStage, DifficultyRating, NaviInfo } from "../types/InfoTypes";


export const initialState: NaviInfo = {
  steps: {} as CookingStage,
  ingredients: {},
  sceneList: {},
  difficulty: {} as DifficultyRating,
  transcript: "",
};

// load the data async
const setDataSlice = createSlice({
  name: "setData",
  initialState,
  reducers: {
    addNewIngredient: (state, action) => {
      console.log(action.payload)
      state.ingredients = { ...state.ingredients, ...action.payload };
    }
  },
  extraReducers: (builder) => {
    builder.addCase(loadDataAsync.fulfilled, (state, action) => {
      state.steps = action.payload.steps;
      state.ingredients = action.payload.ingredients;
      state.sceneList = action.payload.scene_list;
      state.difficulty = action.payload.difficulty;
      state.transcript = action.payload.transcript;
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

export const { addNewIngredient } = setDataSlice.actions;

export default setDataSlice.reducer;
