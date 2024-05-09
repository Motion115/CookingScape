import { Button, Flex, InputNumber, Radio, Space, Typography } from "antd";
import React, { memo, useEffect, useState } from "react";
import {
  DeleteOutlined,
  SwapOutlined,
  DragOutlined,
  FieldTimeOutlined,
} from "@ant-design/icons";
import { Handle, NodeToolbar, Position, useReactFlow } from "reactflow";
import { AppDispatch, RootState } from "../store";
import { setVideoClip } from "../reducers/playerStateReducer";
import { useDispatch, useSelector } from "react-redux";
import { NodeDataParams } from "../types/InfoTypes";

const { Text } = Typography;

interface CustomColorPickerNodeProps {
  data: NodeDataParams;
  isConnectable: boolean;
}

const milestoneBgColor: { [key: string]: string } = {
  Preparation: "#BDD2FD40",
  Cooking: "#FFD8B840",
  Assembly: "#BDEFDB40",
};

export default memo((props: CustomColorPickerNodeProps) => {
  const { data, isConnectable } = props;
  const reactFlow = useReactFlow();

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
        <Space direction="vertical" size="small">
          <div>
            <Text strong={true}>Step: </Text>
            <Text
              editable={{
                onChange: (value: string) => {
                  setDescription(value);
                  // need to sync with the data store (maybe use redux here)
                },
              }}
            >
              {nodeState.description}
            </Text>
          </div>
          <div style={{ padding: "1%" }}>
            <Space direction="horizontal">
              <Text strong={true}>Start Time: </Text>
              <InputNumber
                value={nodeState.time.startTime}
                onChange={(value) => setStartTime(value as number)}
              />
              <Button
                shape="circle"
                icon={<FieldTimeOutlined />}
                onClick={() => {
                  setStartTime(Math.floor(currentTime.time));
                }}
              />

              <Text strong={true}>Duration: </Text>
              <InputNumber
                value={nodeState.time.duration}
                onChange={(value) => setDuration(value as number)}
              />
              <Button
                shape="circle"
                icon={<FieldTimeOutlined />}
                onClick={() => {
                  setDuration(
                    Math.floor(currentTime.time) - nodeState.time.startTime >= 0
                      ? Math.floor(currentTime.time) - nodeState.time.startTime
                      : nodeState.time.duration
                  );
                }}
              />
            </Space>
            <Flex justify="space-between" align="center">
              <Button
                shape="circle"
                icon={<SwapOutlined />}
                onClick={transfer}
              />
              <div className="custom-drag-handle">
                <Button shape="circle" icon={<DragOutlined />} />
              </div>
            </Flex>
          </div>
        </Space>
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
