export interface NaviInfo {
  steps: CookingStage;
  ingredients: ingredientsItem[];
  sceneList: SceneListItem;
  difficulty: DifficultyRating;
  transcript: string;
}

export interface DifficultyRating {
  rating: number,
  reason: string
}

export interface CookingStage {
  preparation: IndividualStep;
  cooking: IndividualStep;
  assembly: IndividualStep;
  sequential: IndividualStep;
}

export interface IndividualStep {
  [key: string]: RecipeStepDescription;
}

export interface RecipeStepDescription {
  description: string;
  clip_id: number[];
  category?: string;
}

export interface SceneListItem {
  [key: string]: {
    startTime: number;
    duration: number;
    endTime: number;
  }
}

export interface VideoState {
  startTime: number;
  duration: number;
  timeStamp?: number;
}

export interface VideoTime {
  time: number
}

export interface ingredientsItem {
  ingredient: string,
  similarity_vector: number[],
  checked: boolean
}

export interface NodeDataParams {
  description: string,
  time: VideoState,
  stage: string,
  node_id: string,
  deleteNode: any,
  updateNode: any
}

export interface APIPostData {
  description: string,
}

export interface APIIngredientVis {
  ingredient: string
}

export interface APIIngredientReplacer extends APIIngredientVis {
  usedIngredient: string;
  transcript: string;
}

export interface IngredientReplacer {
  ingredientUse: string;
  ingredientAlter?: {
    isReplacable: boolean,
    explaination: string
  }
}