import React, {useState} from "react";
import { Typography, Flex, Button, Divider } from "antd";
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
      <Flex vertical={false} align="center">
        <TagChecker videoItems={videoItems} />
        <Text style={{ textAlign: "justify"}}>{stepDescription}</Text>
        {/* <Button shape="circle" size="small">
          <DownOutlined />
        </Button> */}
      </Flex>
      <Divider style={{ margin: "8px 0 0 0"}} />
    </>
  );
};

export default StepItem;
