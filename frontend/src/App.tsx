import React, { useEffect } from "react";
import { Layout, ConfigProvider, Typography, Row, Col, Button, FloatButton, Drawer, Divider, Switch } from "antd";
import THEME from "./looks/theme";
import VideoPlayer from "./modules/videoPlayer";
import IngredientMap from "./modules/IngredientMap";
import RecipeSteps from "./modules/RecipeSteps";
import MilestoneSteps from "./modules/MilestoneSteps";
import {
  InfoCircleOutlined
} from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "./store";
import { loadDataAsync } from "./reducers/setDataReducer";
import MilestoneInterfaceSeq from "./modules/MilestoneStepsSeq";

const { Header, Content, Footer } = Layout;
const { Text, Paragraph } = Typography;

const App: React.FC = () => {
  // const configData = useSelector((state: RootState) => state.setData);
  const dispatch = useDispatch<AppDispatch>();

  // const video = "Wolfgang-Gazpacho";
  // const folder = "./data/.cacheTest/" + video + "/";
  const video = "GR-SzechuanChicken";
  const folder = "./data/" + video + "/";

  const loadData = () => {
    dispatch(loadDataAsync(folder + "video_info.json"));
  }

  useEffect(() => {
    loadData();
  })

  const [isInfoOpen, setIsInfoOpen] = React.useState(false);
  const [switchSeq, setSwitchSeq] = React.useState(true);

  return (
    <div className="app">
      <ConfigProvider theme={THEME}>
        {/* <Header>
          <Text style={{ fontSize: "20px", padding: "1%", fontWeight: "bold" }}>
            CookingNavigator
          </Text>
        </Header> */}
        <Content style={{ padding: "1%", margin: "0 auto" }}>
          <Layout dir="vertical">
            <Row gutter={[16, 24]}>
              <Col span={12}>
                <VideoPlayer videoName={folder + video + ".mp4"} />
              </Col>
              <Col span={12}>
                <IngredientMap />
              </Col>
              <Col span={18}>
                {/* <Switch value={switchSeq} onClick={() => setSwitchSeq(!switchSeq)}></Switch> */}
                <div style={{ width: "100%", height: "420px" }}>
                  {switchSeq ? <MilestoneInterfaceSeq /> : <MilestoneSteps />}
                </div>
              </Col>
              <Col span={6}>
                <div style={{ width: "100%", height: "420px", overflow: 'scroll' }}>
                  <RecipeSteps />
                </div>
              </Col>
            </Row>
          </Layout>
          <FloatButton
            icon={<InfoCircleOutlined />}
            type="default"
            style={{ left: 20, top: 20 }}
            onClick={() => setIsInfoOpen(true)}
          />
          <Drawer
            title="Instructions"
            onClose={() => setIsInfoOpen(false)}
            open={isInfoOpen}
          >
            <Paragraph>
              Reconnect the lines: drag the end with the triangle and connect to
              another node.
              <br />
              Delete the line: drag the end and drop anywhere.
            </Paragraph>
          </Drawer>
        </Content>
        {/* <Footer style={{ height: "80px", padding: "1%", margin: "0 auto" }}>
          © This project is in development stage. All rights reserved.
        </Footer> */}
      </ConfigProvider>
    </div>
  );
};

export default App;
