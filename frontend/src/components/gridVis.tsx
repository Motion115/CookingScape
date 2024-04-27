import * as d3 from "d3";
import React, { useMemo } from "react";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../store";
import { setVideoClip } from "../reducers/playerStateReducer";
import { Tooltip } from "antd";
import { round } from "lodash";

interface GridVisProps {
  data: number[];
  width: number;
}

export default function GridVis(props: GridVisProps) {
  const { data, width } = props;
  const configData = useSelector((state: RootState) => state.setData);
  const sceneList = configData.sceneList;

  const dispatch = useDispatch<AppDispatch>();

  const xScale = useMemo(() => {
    const idx = data.map((d, i) => i.toString());
    return d3.scaleBand().domain(idx).range([0, width]);
  }, [data, width]);

  const dataRange = d3.extent(data) as number[];
  const colorScale = d3.scaleDiverging(
    [dataRange[0], (dataRange[0] + dataRange[1]) / 2, dataRange[1]],
    d3.interpolateRdBu
  );

  const allShapes = data.map((d, i) => {
    const x = xScale(i.toString());
    const y = 5;
    if (d === null || !x || !y) {
      return <React.Fragment key={i}></React.Fragment>;
    }
    return (
        <Tooltip
          title={"Relavance: " + round(d, 2).toString()}
          color={colorScale(d)}
          key={i}
        >
          <rect
            key={i}
            x={x}
            y={y}
            width={xScale.bandwidth()}
            height={10}
            fill={colorScale(d)}
            onClick={(e) => {
              const clipInfo = sceneList[i + 1];
              dispatch(setVideoClip(clipInfo));
            }}
          />
        </Tooltip>
    );
  });

  return (
      <svg height={12} width={width}>
        {allShapes}
      </svg>
  );
}
