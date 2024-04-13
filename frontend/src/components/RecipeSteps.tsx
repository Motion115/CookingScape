import React, { useRef } from "react";
import { useSelector } from "react-redux";
import { RootState } from "../store";
import { Button, Typography } from "antd";

const { Text } = Typography;

interface RecipeSteps {
  preparation: Object;
  cooking: Object;
  assembly: Object;
  sequential: Object;
}

interface RecipeStep {
  description: string;
  clip_id: number[];
}

export default function RecipeSteps() {
  const configData = useSelector((state: RootState) => state.setData);
  const seqentialRecipe = configData.steps as RecipeSteps;
  console.log(seqentialRecipe.sequential)

  return (
    <div>
      {seqentialRecipe.sequential && Object.entries(seqentialRecipe.sequential).map((step: any, index: number) => {
        let [key, val] = step
        
        let value = val as RecipeStep;
        return (
          <div key={index}>
            <Text>{index + 1}.{" "}</Text>
            <Text>{value.description}</Text>
          </div>
        )
      })}
    </div>
  );
}
