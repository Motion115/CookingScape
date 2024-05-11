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
  Rate,
  Affix,
  Popover,
  Modal,
  Input,
} from "antd";
import {
  RedoOutlined,
  CloseOutlined,
  PlusOutlined,
  QuestionOutlined,
} from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../store";
import lodash, { drop } from "lodash";
import GridVis from "../components/gridVis";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWandMagicSparkles } from "@fortawesome/free-solid-svg-icons";
import { SERVER_URL } from "../consts/server";
import { APIIngredientVis, ingredientsItem } from "../types/InfoTypes";
import axios from "axios";
import { addNewIngredient } from "../reducers/setDataReducer";

const { Text } = Typography;

interface IngredientTag {
  ingredient: string;
  checked: boolean;
}

export default function IngredientMap() {
  const configData = useSelector((state: RootState) => state.setData);
  const ingredientList = configData.ingredients;
  const difficultyRating = configData.difficulty;

  const [ingredientTag, setIngredientTag] = useState<IngredientTag[]>([]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newIngredientInput, setNewIngredientInput] = useState("");

  const componentRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(200);
const dispatch = useDispatch<AppDispatch>();
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

  const handleTagClick = (ingredient: string) => {
    // if there is duplicate, only use the first one
    let newState = ingredientTag.map((item) => {
      if (item.ingredient === ingredient) {
        return {
          ingredient: item.ingredient,
          checked: !item.checked,
        };
      }
      return item;
    });
    setIngredientTag(newState);
  };

  const deleteIngredient = (ingredient: string) => {
    let newState = ingredientTag.filter((item) => {
      return item.ingredient !== ingredient;
    });
    setIngredientTag(newState);
  };

  const refreshSimilarityBar = async () => {
    // call the language grounding API
    try {
      const response = await axios.post<APIIngredientVis>(
        SERVER_URL + "/ingredientVideoSim",
        {
          ingredient: newIngredientInput,
        }
      );
      const responseData = response.data as unknown as ingredientsItem; // Parsed JSON response
      dispatch(addNewIngredient(responseData))
    } catch (error) {
      console.error("Error fetching data:", error);
    }
    // set state to update the time
  };

  const generateTags = () => {
    return lodash.map(ingredientTag, (item: IngredientTag) => {
      return (
        <Tag
          color={item.checked ? "#1B7BFF" : "white"}
          key={item.ingredient}
          onClick={() => handleTagClick(item.ingredient)}
          closeIcon={
            <CloseOutlined
              style={{ color: item.checked ? "white" : "black" }}
            />
          }
          onClose={() => deleteIngredient(item.ingredient)}
          style={{
            color: item.checked ? "white" : "black",
          }}
        >
          {item.ingredient}
        </Tag>
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

  const addIngredient = () => {
    setIsModalOpen(true);
  }

  return (
    <div ref={componentRef}>
      <Space direction="vertical">
        <div>
          Refresh width:{" "}
          <Button onClick={handleResize} shape="circle">
            <RedoOutlined />
          </Button>
        </div>
        <div>
          <Flex gap="small" align="center">
            <Text>Difficulty</Text>
            <Rate count={3} value={difficultyRating.rating} disabled />
            <Popover
              content={
                <div style={{ width: "300px", textAlign: "justify" }}>
                  <Text>{difficultyRating.reason}</Text>
                </div>
              }
              title="Why this difficulty rating?"
              placement="bottom"
            >
              <Button size="small" type="text">
                Why this difficulty rating
                <QuestionOutlined />
              </Button>
            </Popover>
          </Flex>
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
            <Tag
              style={{
                borderStyle: "dashed",
              }}
              icon={<PlusOutlined />}
              onClick={addIngredient}
            >
              Add Ingredient
            </Tag>
            <Modal
              title="Add Ingredient"
              open={isModalOpen}
              onOk={() => setIsModalOpen(false)}
              onCancel={() => setIsModalOpen(false)}
            >
              <Space.Compact>
                <Input
                  placeholder="Enter Ingredient"
                  onChange={(e) => setNewIngredientInput(e.target.value)}
                />
                <Button
                  onClick={() => refreshSimilarityBar()}
                  icon={<FontAwesomeIcon icon={faWandMagicSparkles} />}
                />
              </Space.Compact>
            </Modal>
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
