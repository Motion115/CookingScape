import React, {useState} from "react";
import { Typography, Flex, Button } from "antd";
import { DownOutlined } from "@ant-design/icons";
import TagChecker from "./tagChecker";
import { VideoState } from "../types/InfoTypes";

const { Text } = Typography;

interface StepItemProps {
  stepDescription: string;
  videoItems: VideoState[]
}

const StepItem: React.FC<StepItemProps> = (props: StepItemProps) => {
  const { stepDescription, videoItems } = props;

  return (
    <>
      <Flex vertical={false}>
        <TagChecker videoItems={videoItems} />
        <Text>{stepDescription}</Text>
        <Button shape="circle" size="small">
          <DownOutlined />
        </Button>
      </Flex>
    </>
  );
};

export default StepItem;
