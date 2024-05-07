import { Button, Flex, InputNumber, Radio, Space, Typography } from "antd";
import React, { memo, useState } from "react";
import { DeleteOutlined, SwapOutlined, DragOutlined, FieldTimeOutlined } from "@ant-design/icons";
import { Handle, NodeToolbar, Position, useReactFlow } from "reactflow";
import { AppDispatch, RootState } from "../store";
import { setVideoClip } from "../reducers/playerStateReducer";
import { useDispatch, useSelector } from "react-redux";

const { Text } = Typography;

interface CustomColorPickerNodeProps {
  data: any;
  isConnectable: boolean;
}

const milestoneBgColor: { [key: string]: string } = {
  Preparation: "#BDD2FD40",
  Cooking: "#FFD8B840",
  Assembly: "#BDEFDB40",
};

export default memo((props: CustomColorPickerNodeProps) => {
  const { data, isConnectable } = props;

  const [startTime, setStartTime] = useState<number>(
    Math.floor(data.time.startTime) as number
  );
  const [duration, setDuration] = useState<number>(
    data.time.duration as number
  );

  const [description, setDescription] = useState<string>(
    data.data.description
  );

  const [stage, setStage] = useState<string>(data.stage as string);
  const currentTime = useSelector((state: RootState) => state.playerTime);
  const dispatch = useDispatch<AppDispatch>();

  const transfer = () => {
    dispatch(
      setVideoClip({
        startTime: startTime,
        duration: duration,
      })
    );
  };

  const onDeleteNode = () => {
    data.deleteFunc(data.node_id);
  }

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
            value={stage}
            defaultValue={stage}
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
          backgroundColor: milestoneBgColor[stage],
          border: "1px solid #555",
          width: "400px",
          borderRadius: "12px",
        }}
      >
        <Space direction="vertical" size="small">
          <div>
            <Text strong={true}>Step: </Text>
            <Text editable={{ onChange: (value: string) => {
              setDescription(value)
              // need to sync with the data store (maybe use redux here)
             } }}>{description}</Text>
          </div>
          <div style={{ padding: "1%" }}>
            <Space direction="horizontal">
              <Text strong={true}>Start Time: </Text>
              <InputNumber
                value={startTime}
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
                value={duration}
                onChange={(value) => setDuration(value as number)}
              />
              <Button
                shape="circle"
                icon={<FieldTimeOutlined />}
                onClick={() => {
                  setDuration(
                    Math.floor(currentTime.time) - startTime >= 0
                      ? Math.floor(currentTime.time) - startTime
                      : duration
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
