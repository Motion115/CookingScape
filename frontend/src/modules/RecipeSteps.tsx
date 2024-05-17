import React, { useRef } from "react";
import { useSelector } from "react-redux";
import { RootState } from "../store";
import { Button, Typography, Space } from "antd";
import TagChecker from "../components/tagChecker";
import StepItem from "../components/stepItem";
import { CookingStage, RecipeStepDescription } from "../types/InfoTypes";

import lodash from "lodash";

const { Text } = Typography;

export default function RecipeSteps() {
  const configData = useSelector((state: RootState) => state.setData);
  const seqentialRecipe = configData.steps.sequential;

  const sceneList = configData.sceneList

  return (
    <div>
      <Space direction="vertical" size="small">
        {seqentialRecipe &&
          lodash.map(
            seqentialRecipe,
            (val: RecipeStepDescription, key: string) => {
              let clipRecord = val.clip_id.slice(0, 3).map((val: number) => {
                return sceneList[val.toString()]
              })
              return (
                <StepItem
                  stepDescription={val.description}
                  videoItems={clipRecord}
                  key={key}
                />
              );
            }
          )}
      </Space>
    </div>
  );
}
