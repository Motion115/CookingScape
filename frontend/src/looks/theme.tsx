import { Divider, Layout } from "antd";

const THEME = {
  token: {
    // colorPrimary: "#00B96B",
    // colorPrimary: "blue",
    colorBgLayout: "#ffffff",
    borderRadius: 4,
    fontSize: 16,
    colorSplit: "rgba(25, 25, 25, 0.4)",
    fontFamily:
      "Maven Pro, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue'",
  },
  components: {
    Layout: {
      headerBg: "#ffffff",
      headerPadding: 0,
      footerPadding: "50px 0px 50px 0px",
      headerHeight: 35,
    },
    Menu: {
      itemBorderRadius: 12,
      subMenuItemBorderRadius: 6,
      horizontalItemBorderRadius: 8,
    },
    Slider: {
      trackBg: "#000000",
      trackHoverBg: "#000000",
      railBg: "rgba(0, 0, 0, 0.2)",
      railHoverBg: "rgba(0, 0, 0, 0.4)",
      handleColor: "#000000",
      handleActiveColor: "#000000",
      dotBorderColor: "#000000",
      dotActiveBorderColor: "#000000",
    },
    Tag: {
      defaultBg: "#fafafa",
    },
  },
};

export default THEME;
