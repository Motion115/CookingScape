import React, { useEffect } from "react";
import { Layout, ConfigProvider, Typography, Row, Col, Button } from "antd";
import THEME from "./looks/theme";
import VideoPlayer from "./components/videoPlayer";
import IngredientMap from "./components/IngredientMap";
import RecipeSteps from "./components/RecipeSteps";
import MilestoneSteps from "./components/MilestoneSteps";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "./store";
import { loadDataAsync } from "./reducers/setDataReducer";

const { Header, Content, Footer } = Layout;
const { Text } = Typography;

const App: React.FC = () => {
  // const configData = useSelector((state: RootState) => state.setData);
  const dispatch = useDispatch<AppDispatch>();

  const loadData = () => {
    dispatch(loadDataAsync("./video_info.json"));
  }

  useEffect(() => {
    loadData();
  })

  return (
    <div className="app">
      <ConfigProvider theme={THEME}>
        <Header>
          <Text style={{ fontSize: "20px", padding: "2%", fontWeight: "bold" }}>
            CookingNavigator
          </Text>
        </Header>
        <Content style={{ padding: "2%", margin: "0 auto" }}>
          <Layout dir="vertical">
            <Row gutter={[16, 24]}>
              <Col span={12}>
                <VideoPlayer />
              </Col>
              <Col span={12}>
                <IngredientMap />
              </Col>
            </Row>
            <Row gutter={[16, 24]}>
              <Col span={12}>
                <RecipeSteps />
              </Col>
              <Col span={12}>
                <MilestoneSteps />
              </Col>
            </Row>
          </Layout>
        </Content>
        <Footer style={{ height: "80px", padding: "2%", margin: "0 auto" }}>
          © This project is in developmenet stage. All rights reserved.
        </Footer>
      </ConfigProvider>
    </div>
  );
};

export default App;
