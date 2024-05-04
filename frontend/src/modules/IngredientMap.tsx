import React, { useRef, useEffect, useState } from "react";
import {
  Button,
  Typography,
  Space,
  Flex,
  Tooltip,
  Dropdown,
  Tag,
  Select,
} from "antd";
import { RedoOutlined, CloseOutlined } from "@ant-design/icons";
import { useSelector } from "react-redux";
import { RootState } from "../store";
import lodash, { drop } from "lodash";
import GridVis from "../components/gridVis";

const { Text } = Typography;

interface IngredientTag {
  ingredient: string;
  checked: boolean;
}

export default function IngredientMap() {
  const configData = useSelector((state: RootState) => state.setData);
  const ingredientList = configData.ingredients;

  const [ingredientTag, setIngredientTag] = useState<IngredientTag[]>([]);

  const componentRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(200);

  const handleResize = () => {
    const columnWidth = componentRef.current?.clientWidth;
    setWidth(columnWidth || 200);
  };

  useEffect(() => {
    // window.addEventListener("resize", handleResize);
    handleResize();

    const dropDownItems = lodash.map(
      ingredientList,
      (val: number[], key: string) => {
        return {
          ingredient: key,
          checked: false,
        };
      }
    );
    if (dropDownItems.length > 0) {
      dropDownItems[0].checked = true;
    }
    setIngredientTag(dropDownItems);
    // return () => {
    //   window.removeEventListener("resize", handleResize);
    // };
  }, [ingredientList]);

  const handleTagClick = (checked: boolean, ingredient: string) => {
    setIngredientTag((prevState) => {
      const newState = [...prevState];
      const index = newState.findIndex(
        (item) => item.ingredient === ingredient
      );
      if (index !== -1) {
        newState[index].checked = checked;
      }
      return newState;
    });
  };

  const generateTags = () => {
    return lodash.map(ingredientTag, (item: IngredientTag) => {
      return (
        <Tag.CheckableTag
          checked={item.checked}
          key={item.ingredient}
          onChange={(e) => handleTagClick(e, item.ingredient)}
        >
          {item.ingredient}
        </Tag.CheckableTag>
      );
    });
  };
  const ingredientRenderer = () => {
    return (
      <Space direction="vertical">
        {ingredientTag.map((item: IngredientTag) => {
          if (item.checked) {
            const visData = ingredientList[item.ingredient];
            return (
              <div key={item.ingredient}>
                <Text>{item.ingredient}</Text>
                <GridVis data={visData} width={width} />
              </div>
            );
          }
          return null;
        })}
      </Space>
    );
  };

  return (
    <div ref={componentRef}>
      <Space direction="vertical">
        <div>
          Refresh width:{" "}
          <Button onClick={handleResize} shape="circle">
            <RedoOutlined />
          </Button>
        </div>
        <div style={{ width: "100%" }}>
          <Flex justify="space-between" wrap="wrap" gap="small">
            {/* <Select
              options={dropDownItems}
              onChange={refreshFilter}
              defaultValue={currentIngredient}
              style={{ width: "60%" }}
            /> */}
            {generateTags()}
          </Flex>
        </div>
        <div>{ingredientRenderer()}</div>

        {/* lodash.map(ingredientList, (val: number[], key: string) => {
            return (
              <div key={key}>
                <Space direction="vertical">
                  <Text>{key}</Text>
                  {/* <GridVis data={val} width={width} /> */}
      </Space>
    </div>
  );
}
