export interface NaviInfo {
  steps: CookingStage;
  ingredients: ingredientsItem;
  sceneList: SceneListItem;
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
}

export interface SceneListItem {
  [key: string]: {
    startTime: number;
    duration: number
  }
}

export interface VideoState {
  startTime: number;
  duration: number;
}

export interface ingredientsItem {
  [key: string]: number[]
}