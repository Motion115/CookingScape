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
      state.ingredients = { ...state.ingredients, ...action.payload };
      // console.log(action.payload);
    },
    replaceExistingIngredient: (state, action) => {
      // delete action.payload.pickedIngredient
      // console.log(action.payload);
      let newList = { ...state.ingredients, ...action.payload.responseData };
      delete newList[action.payload.pickedIngredient];
      state.ingredients = newList;
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

export const { addNewIngredient, replaceExistingIngredient } = setDataSlice.actions;

export default setDataSlice.reducer;
