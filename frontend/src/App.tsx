import React from 'react';
import { Layout, ConfigProvider, Typography, Row, Col } from 'antd';
import THEME from './looks/theme';
import VideoPlayer from './components/videoPlayer';

const { Header, Content, Footer } = Layout;
const { Text } = Typography;

const App: React.FC = () => {
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
              <Col span={12}>Ingredient canvas</Col>
            </Row>
            <Row gutter={[16, 24]}>
              <Col span={12}>Step-by-step canvas</Col>
              <Col span={12}>milestone canvas</Col>
            </Row>
          </Layout>
        </Content>
        <Footer style={{ height: "80px", padding: "2%", margin: "0 auto" }}>
          © This project is in developmenet stage. All rights reserved.
        </Footer>
      </ConfigProvider>
    </div>
  );
}

export default App;