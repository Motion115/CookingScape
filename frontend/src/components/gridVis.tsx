import * as d3 from "d3";
import React from "react";
import { useEffect } from "react";

interface GridVisProps {
  data: number[];
}

export default function GridVis(props: GridVisProps) {
  const { data } = props;

  const svgRef = React.useRef(null);

  useEffect(() => {
    const svgElement = d3.select(svgRef.current);
    svgElement.selectAll("*").remove();

    const dataRange = d3.extent(data) as number[];
    const colorScale = d3.scaleDiverging([dataRange[0], (dataRange[0] + dataRange[1]) / 2, dataRange[1]], d3.interpolateRdBu);



    const svgWidth = 900;
    const rectangleWidth = svgWidth / data.length;
    const rectangleHeight = 10;
    const gap = 0;
        console.log(rectangleWidth);

    svgElement
      .selectAll("rect")
      .data(data)
      .enter()
      .append("rect")
      .attr("x", (_, i) => i * rectangleWidth)
      .attr("y", 0)
      .attr("width", rectangleWidth - gap)
      .attr("height", rectangleHeight)
      .attr("fill", (d) => colorScale(d))
      .attr("data-index", (_, i) => i) // 设置data-index属性存储索引值
      .on("click", (event, d) => {
        const clickedIndex = d3.select(event.target).attr("data-index");
        console.log("Clicked:", clickedIndex);
      });
  }, [data]);

  return <svg ref={svgRef} height={12} width={1000}/>;
}
