import { createAsyncThunk, createSlice, current } from "@reduxjs/toolkit";
import { CookingStage, DifficultyRating, NaviInfo, ingredientsItem } from "../types/InfoTypes";
import lodash from "lodash";

export const initialState: NaviInfo = {
  steps: {} as CookingStage,
  ingredients: [] as ingredientsItem[],
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
      state.ingredients = [ ...state.ingredients, action.payload ];
      // console.log(action.payload);
    },
    setIngredientSelection: (state, action) => {
      let ingredient: string = action.payload;
      // find this ingredient in state.ingredients
      let ingredientList: ingredientsItem[] = state.ingredients;
      ingredientList = ingredientList.map((item: ingredientsItem) => {
        if (item.ingredient === ingredient) {
          item.checked = !item.checked;
        }
        return item;
      })
      state.ingredients = ingredientList;
    },
    replaceExistingIngredient: (state, action) => {
      // delete action.payload.pickedIngredient
      // console.log(action.payload);
      let currentList = state.ingredients;
      currentList = currentList.map((item: ingredientsItem) => {
        if (item.ingredient === action.payload.pickedIngredient) {
          return action.payload.processedResp;
        }
        return item;
      })
      // lodash.uniq
      currentList = lodash.uniqBy(currentList, 'ingredient');
      state.ingredients = currentList;
    },
    deleteSelectedIngredient: (state, action) => {
      let currentList = state.ingredients;
      currentList = currentList.filter((item: ingredientsItem) => {
        return item.ingredient !== action.payload;
      })
      state.ingredients = currentList;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(loadDataAsync.fulfilled, (state, action) => {
      state.steps = action.payload.steps;
      // state.ingredients = action.payload.ingredients;
      state.sceneList = action.payload.scene_list;
      state.difficulty = action.payload.difficulty;
      state.transcript = action.payload.transcript;

      let ingredientList = action.payload.ingredients;
      let dropDownItems: ingredientsItem[] = lodash.map(
        ingredientList,
        (val: number[], key: string) => {
          return {
            ingredient: key,
            similarity_vector: val,
            checked: false,
          };
        }
      );
      if (dropDownItems.length > 0) {
        dropDownItems[0].checked = true;
      }
      state.ingredients = dropDownItems;
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

export const {
  addNewIngredient,
  replaceExistingIngredient,
  deleteSelectedIngredient,
  setIngredientSelection
} = setDataSlice.actions;

export default setDataSlice.reducer;
