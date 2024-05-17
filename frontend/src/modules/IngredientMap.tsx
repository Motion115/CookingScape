import React, { useRef, useEffect, useState, useMemo } from "react";
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
  Radio,
  Divider,
} from "antd";
import {
  RedoOutlined,
  CloseOutlined,
  PlusOutlined,
  QuestionOutlined,
  SwapOutlined,
  CheckCircleTwoTone,
  CloseCircleTwoTone,
} from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../store";
import lodash, { drop } from "lodash";
import GridVis from "../components/gridVis";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWandMagicSparkles } from "@fortawesome/free-solid-svg-icons";
import { SERVER_URL } from "../consts/server";
import {
  APIIngredientVis,
  IngredientReplacer,
  ingredientsItem,
} from "../types/InfoTypes";
import axios from "axios";
import {
  addNewIngredient,
  deleteSelectedIngredient,
  replaceExistingIngredient,
  setIngredientSelection,
} from "../reducers/setDataReducer";

const { Text, Paragraph } = Typography;

export default function IngredientMap() {
  const configData = useSelector((state: RootState) => state.setData);
  const ingredientList = configData.ingredients;
  const transcript = configData.transcript;

  const [isLoading, setIsLoading] = useState(false);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isIngredientModalOpen, setIsIngredientModalOpen] = useState(false);

  const [pickedIngredient, setPickedIngredient] = useState("");
  const [newIngredientInput, setNewIngredientInput] = useState("");
  const [replaceIngredient, setReplaceIngredient] =
    useState<IngredientReplacer | null>(null);

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
    // return () => {
    //   window.removeEventListener("resize", handleResize);
    // };
  }, [ingredientList]);

  const handleTagClick = (ingredient: string) => {
    dispatch(setIngredientSelection(ingredient));
  };

  const deleteIngredient = (ingredient: string) => {
    dispatch(deleteSelectedIngredient(ingredient));
  };

  const refreshSimilarityBar = async (mode: "add" | "replace" = "add") => {
    setIsLoading(true);
    // call the language grounding API
    try {
      const response = await axios.post<APIIngredientVis>(
        SERVER_URL + "/ingredientVideoSim",
        {
          ingredient: newIngredientInput,
        }
      );
      const responseData = response.data as unknown as {[key: string]: number[]}; // Parsed JSON response
      let processedResp: ingredientsItem = {
        ingredient: Object.keys(responseData)[0],
        similarity_vector: responseData[Object.keys(responseData)[0]],
        checked: false
      }
      if (mode === "add") dispatch(addNewIngredient(processedResp));
      else if (mode === "replace") {
        dispatch(replaceExistingIngredient({ processedResp, pickedIngredient }));
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    }
    // set state to update the time
    setIsLoading(false);
  };

  const queryReplacement = async () => {
    setIsLoading(true);
    // call the language grounding API
    try {
      const response = await axios.post<APIIngredientVis>(
        SERVER_URL + "/ingredientReplacer",
        {
          usedIngredient: pickedIngredient,
          ingredient: newIngredientInput,
          transcript: transcript,
        }
      );
      const responseData = response.data as unknown as IngredientReplacer; // Parsed JSON response
      setReplaceIngredient(responseData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
    setIsLoading(false);
  };

  const ingredientReplacer = () => {
    queryReplacement();
    // refreshSimilarityBar();
  };

  const generateTags = () => {
    if (Array.isArray(ingredientList)) {
    return ingredientList.map((item: ingredientsItem) => {
      return (
        <Tag
          color={item.checked ? "#1B7BFFcc" : "white"}
          key={item.ingredient}
          onDoubleClick={() => {
            if (item.checked) {
              handleTagClick(item.ingredient);
            }
            setIsIngredientModalOpen(true);
            setPickedIngredient(item.ingredient);
          }}
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
          <Radio
            checked={item.checked}
            onClick={() => handleTagClick(item.ingredient)}
          />
          {item.ingredient}
        </Tag>
      );
    });
  }
  };

  const ingredientRenderer = () => {
    if (Array.isArray(ingredientList)) {
    return (
      <Space direction="vertical">
        {ingredientList && ingredientList.map((item: ingredientsItem) => {
          if (item.checked) {
            const visData = item.similarity_vector;
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
  }
  };

  const replacementRenderer = (replaceIngredient: IngredientReplacer) => {
    if (replaceIngredient.ingredientAlter?.isReplacable === true) {
      return (
        <div>
          <Space direction="horizontal">
            <CheckCircleTwoTone twoToneColor="#52c41a" />
            Replacable!
            <Button
              onClick={() => refreshSimilarityBar("replace")}
              size="small"
              loading={isLoading}
            >
              Replace
            </Button>
          </Space>
        </div>
      );
    } else if (replaceIngredient.ingredientAlter?.isReplacable === false) {
      return (
        <div>
          <Space direction="horizontal">
            <CloseCircleTwoTone twoToneColor="red" /> Not Replacable!
            <Button
              onClick={() => refreshSimilarityBar("replace")}
              size="small"
              loading={isLoading}
            >
              Replace Anyways
            </Button>
          </Space>
        </div>
      );
    }
  };

  const addIngredient = () => {
    setIsModalOpen(true);
  };

  const clearInputCache = () => {
    setNewIngredientInput("");
    setReplaceIngredient(null);
  };

  const AddIngredientModal = (
    <Modal
      title="Add Ingredient"
      open={isModalOpen}
      onOk={() => {
        setIsModalOpen(false);
        refreshSimilarityBar();
        clearInputCache();
      }}
      onCancel={() => {
        setIsModalOpen(false);
        clearInputCache();
      }}
    >
      <Space.Compact>
        <Input
          placeholder="Enter Ingredient"
          onChange={(e) => setNewIngredientInput(e.target.value)}
          value={newIngredientInput}
        />
        <Button
          onClick={() => refreshSimilarityBar()}
          icon={<FontAwesomeIcon icon={faWandMagicSparkles} />}
        />
      </Space.Compact>
    </Modal>
  );

  return (
    <div ref={componentRef}>
      <Space direction="vertical">
        {/* <div>
          Refresh width:{" "}
          <Button onClick={handleResize} shape="circle">
            <RedoOutlined />
          </Button>
        </div> */}
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
              title="Ingredient Explorer"
              open={isIngredientModalOpen}
              onOk={() => {
                setIsIngredientModalOpen(false);
                clearInputCache();
              }}
              onCancel={() => {
                setIsIngredientModalOpen(false);
                clearInputCache();
              }}
              width={"60%"}
            >
              <Space direction="vertical">
                <Flex align="center" justify="space-between" gap="small">
                  <Input value={pickedIngredient} disabled />
                  <SwapOutlined />
                  <Input
                    placeholder="Enter Query"
                    onChange={(e) => setNewIngredientInput(e.target.value)}
                    value={newIngredientInput}
                  />
                  <Tooltip title="Check ingredient usage">
                    <Button
                      onClick={() => ingredientReplacer()}
                      icon={<FontAwesomeIcon icon={faWandMagicSparkles} />}
                      shape="circle"
                      loading={isLoading}
                    />
                  </Tooltip>
                </Flex>
                {replaceIngredient && (
                  <>
                    {replacementRenderer(replaceIngredient)}
                    <Space direction="horizontal">
                      <div
                        style={{
                          textAlign: "justify",
                          overflow: "scroll",
                          height: "300px",
                        }}
                      >
                        <Text>{replaceIngredient.ingredientUse}</Text>
                      </div>
                      <Divider type="vertical" />
                      <div
                        style={{
                          textAlign: "justify",
                          overflow: "scroll",
                          height: "300px",
                        }}
                      >
                        <Text>
                          {replaceIngredient?.ingredientAlter?.explaination}
                        </Text>
                      </div>
                    </Space>
                  </>
                )}
              </Space>
            </Modal>
            {AddIngredientModal}
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
