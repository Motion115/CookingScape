import {
  Button,
  Divider,
  Flex,
  InputNumber,
  Radio,
  Space,
  Tooltip,
  Typography,
} from "antd";
import React, { memo, useEffect, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWandMagicSparkles } from "@fortawesome/free-solid-svg-icons";
import {
  DeleteOutlined,
  CaretRightOutlined,
  DragOutlined,
  FieldTimeOutlined,
} from "@ant-design/icons";
import { Handle, NodeToolbar, Position, useReactFlow } from "reactflow";
import { AppDispatch, RootState } from "../store";
import { setVideoClip } from "../reducers/playerStateReducer";
import { useDispatch, useSelector } from "react-redux";
import {
  APIPostData,
  NodeDataParams,
  RecipeStepDescription,
} from "../types/InfoTypes";
import { milestoneBgColor, milestoneFgColor } from "../looks/coloring";
import { SERVER_URL } from "../consts/server";
import axios from "axios";

const { Text } = Typography;

interface CustomColorPickerNodeProps {
  data: NodeDataParams;
  isConnectable: boolean;
}

export default memo((props: CustomColorPickerNodeProps) => {
  const { data, isConnectable } = props;
  const reactFlow = useReactFlow();

  const configData = useSelector((state: RootState) => state.setData);
  const sceneList = configData.sceneList;

  const [nodeState, setNodeState] = useState<NodeDataParams>(data);

  useEffect(() => {
    const nodesListNew = reactFlow.getNodes().map((node) => {
      if (node.id === nodeState.node_id) {
        // reset the data segment
        return { ...node, data: nodeState };
      }
      return node;
    });

    reactFlow.setNodes(nodesListNew);
  }, [nodeState]);

  const setStartTime = (time: number) => {
    setNodeState({
      ...nodeState,
      time: {
        ...nodeState.time,
        startTime: time,
      },
    });
  };

  const setDuration = (time: number) => {
    setNodeState({
      ...nodeState,
      time: {
        ...nodeState.time,
        duration: time,
      },
    });
  };

  const setDescription = (desc: string) => {
    setNodeState({
      ...nodeState,
      description: desc,
    });
  };

  const setStage = (stage: string) => {
    setNodeState({
      ...nodeState,
      stage: stage,
    });
  };

  const currentTime = useSelector((state: RootState) => state.playerTime);
  const dispatch = useDispatch<AppDispatch>();

  const transfer = () => {
    dispatch(
      setVideoClip({
        startTime: nodeState.time.startTime,
        duration: nodeState.time.duration,
      })
    );
  };

  const onDeleteNode = () => {
    data.deleteNode(data.node_id);
  };

  const [vlmLoading, setVlmLoading] = useState(false);
  const callVideoLanguageGrounding = async () => {
    setVlmLoading(true);
    const description = nodeState.description;
    // call the language grounding API
    try {
      const response = await axios.post<APIPostData>(
        SERVER_URL + "/textToClip",
        {
          description: description,
        }
      );
      const responseData = response.data as RecipeStepDescription; // Parsed JSON response

      // console.log(sceneList[responseData.clip_id[0].toString()]);
      setNodeState({
        ...nodeState,
        time: sceneList[responseData.clip_id[0].toString()],
      });
      setVlmLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
    // set state to update the time
  };

  return (
    <>
      <NodeToolbar position={Position.Top}>
        <Space direction="horizontal">
          <Radio.Group
            options={[
              {
                label: "Preparation",
                value: "Preparation",
              },
              {
                label: "Cooking",
                value: "Cooking",
              },
              {
                label: "Assembly",
                value: "Assembly",
              },
            ]}
            onChange={(e) => {
              setStage(e.target.value as string);
            }}
            value={nodeState.stage}
            defaultValue={nodeState.stage}
            optionType="button"
            buttonStyle="solid"
          />
        </Space>
      </NodeToolbar>
      <NodeToolbar position={Position.Bottom}>
        <Button
          shape="circle"
          danger
          size="large"
          icon={<DeleteOutlined />}
          onClick={onDeleteNode}
        />
      </NodeToolbar>
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: "#555" }}
        onConnect={(params) => console.log("handle onConnect", params)}
        isConnectable={isConnectable}
        id="tar"
      />
      <div
        style={{
          backgroundColor: milestoneBgColor[nodeState.stage],
          border: "1px solid #555",
          width: "400px",
          borderRadius: "12px",
        }}
      >
        <div
          style={{
            width: "90%",
            margin: "auto",
            padding: "1%",
            textAlign: "justify",
            backgroundColor: milestoneFgColor[nodeState.stage],
            borderRadius: "12px",
          }}
        >
          <Flex justify="space-between" align="center">
            <Text
              strong
              editable={{
                onChange: (value: string) => {
                  setDescription(value);
                  // need to sync with the data store (maybe use redux here)
                },
              }}
            >
              {nodeState.description}
            </Text>
            <Divider type="vertical" />
            <Tooltip title="Transfer to this step" color="blue">
              <Button
                shape="circle"
                icon={<CaretRightOutlined />}
                onClick={transfer}
              />
            </Tooltip>
          </Flex>
        </div>
        <Divider
          style={{ margin: "auto", width: "90%", padding: "0%" }}
          dashed
        />

        <div
          style={{
            width: "90%",
            margin: "auto",
            padding: "1%",
            textAlign: "justify",
          }}
        >
          <Flex justify="space-between" align="center">
            <Space direction="vertical">
              <div>
                <Space direction="horizontal">
                  <Text>From: </Text>
                  <InputNumber
                    value={nodeState.time.startTime}
                    onChange={(value) => setStartTime(value as number)}
                  />
                  <Text> seconds</Text>
                  <Tooltip title="Record current play time" color="blue">
                    <Button
                      shape="circle"
                      icon={<FieldTimeOutlined />}
                      onClick={() => {
                        setStartTime(Math.floor(currentTime.time));
                      }}
                    />
                  </Tooltip>
                </Space>
              </div>

              <div>
                <Space direction="horizontal">
                  <Text>For: </Text>
                  <InputNumber
                    value={nodeState.time.duration}
                    onChange={(value) => setDuration(value as number)}
                  />
                  <Text> seconds</Text>
                  <Tooltip title="Record current play time" color="blue">
                    <Button
                      shape="circle"
                      icon={<FieldTimeOutlined />}
                      onClick={() => {
                        setDuration(
                          Math.floor(currentTime.time) -
                            nodeState.time.startTime >=
                            0
                            ? Math.floor(currentTime.time) -
                                nodeState.time.startTime
                            : nodeState.time.duration
                        );
                      }}
                    />
                  </Tooltip>
                </Space>
              </div>
            </Space>
            <Space direction="horizontal">
              <Tooltip title="Auto refocus video segment" color="blue">
                <Button
                  shape="circle"
                  icon={<FontAwesomeIcon icon={faWandMagicSparkles} />}
                  onClick={callVideoLanguageGrounding}
                  loading={vlmLoading}
                />
              </Tooltip>
              <div className="custom-drag-handle">
                <Tooltip title="Drag to move, click to configure" color="blue">
                  <Button shape="circle" icon={<DragOutlined />} />
                </Tooltip>
              </div>
            </Space>
          </Flex>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        isConnectable={isConnectable}
        id="src"
      />
    </>
  );
});
