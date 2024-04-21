import React, { useRef } from "react";
import { Button, Typography, Space, Flex } from "antd";
import { useSelector } from "react-redux";
import { RootState } from "../store";
import lodash from "lodash";
import GridVis from "../components/gridVis";

const { Text } = Typography;

export default function IngredientMap() {
  const configData = useSelector((state: RootState) => state.setData);
  const ingredientList = configData.ingredients;

  console.log(ingredientList);
  return (
    <>
      <Space direction="vertical">
        {ingredientList &&
          lodash.map(ingredientList, (val: number[], key: string) => {
            return (
              <div key={key}>
                <Space direction="vertical">
                  <Text>{key}</Text>
                  <GridVis data={val} />
                </Space>
              </div>
            );
          })}
      </Space>
    </>
  );
}
