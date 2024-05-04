import React, { useState, useEffect, useCallback } from "react";
import ReactFlow, {
  useNodesState,
  useEdgesState,
  addEdge,
  MiniMap,
  Controls,
  Position,
} from "reactflow";
import "reactflow/dist/style.css";

import videoPlayNode from "../components/videoPlayNode";
import { useSelector } from "react-redux";
import { RootState } from "../store";
import lodash from "lodash";
import { RecipeStepDescription } from "../types/InfoTypes";

const initBgColor = "#1A192B";

const connectionLineStyle = { stroke: "#000" };
const nodeTypes = {
  selectorNode: videoPlayNode,
};

const defaultViewport = { x: 0, y: 0, zoom: 1.5 };

const CustomNodeFlow = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const configData = useSelector((state: RootState) => state.setData);
  const cookingPrep = configData.steps.preparation;
  const sceneList = configData.sceneList;

  useEffect(() => {
    let i = -1;
    let newNodes: any[] = lodash.map(
      cookingPrep,
      (val: RecipeStepDescription, key: string) => {
        let clipRecord = val.clip_id.slice(0, 1).map((val: number) => {
          return sceneList[val.toString()];
        });
        i += 1;
        return {
          id: key,
          type: "selectorNode",
          data: { data: val, time: clipRecord[0], stage: "Preparation" },
          position: { x: 25 + i * 450, y: 10 },
          isConnectable: true,
          // parentNode: "group_prep",
          // extent: "parent",
          dragHandle: ".custom-drag-handle",
        };
      }
    );

    //   let group_node = {
    //     id: 'group_prep',
    //     type: 'group',
    //     position: {
    //       x: 0,
    //       y: 0,
    //     },
    //     style: {
    //       width: 450 * newNodes.length,
    //       height: 180,
    //       backgroundColor: 'rgba(208, 192, 247, 0.2)',
    //   }
    // }

    setNodes([...nodes, ...newNodes]);

    // setNodes([
    //   {
    //     id: "1",
    //     type: "input",
    //     data: { label: "An input node" },
    //     position: { x: 0, y: 50 },
    //     sourcePosition: Position.Bottom,
    //   },
    //   {
    //     id: "2",
    //     type: "selectorNode",
    //     data: { color: initBgColor },
    //     style: { border: "1px solid #777", padding: 10 },
    //     position: { x: 300, y: 50 },
    //   },
    //   {
    //     id: "3",
    //     type: "output",
    //     data: { label: "Output A" },
    //     position: { x: 650, y: 25 },
    //     targetPosition: Position.Left,
    //   },
    //   {
    //     id: "4",
    //     type: "output",
    //     data: { label: "Output B" },
    //     position: { x: 650, y: 100 },
    //     targetPosition: Position.Left,
    //   },
    // ]);

    // setEdges([
    //   {
    //     id: "e1-2",
    //     source: "1",
    //     target: "2",
    //     animated: true,
    //     style: { stroke: "#fff" },
    //   },
    //   {
    //     id: "e2a-3",
    //     source: "2",
    //     target: "3",
    //     sourceHandle: "a",
    //     animated: true,
    //     style: { stroke: "#fff" },
    //   },
    //   {
    //     id: "e2b-4",
    //     source: "2",
    //     target: "4",
    //     sourceHandle: "b",
    //     animated: true,
    //     style: { stroke: "#fff" },
    //   },
    // ]);
  }, [cookingPrep]);

  const onConnect = useCallback(
    (params: any) =>
      setEdges((eds) =>
        addEdge({ ...params, animated: true, style: { stroke: "#fff" } }, eds)
      ),
    []
  );
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      nodeTypes={nodeTypes}
      connectionLineStyle={connectionLineStyle}
      // snapToGrid={true}
      // snapGrid={[20, 20]}
      defaultViewport={defaultViewport}
      fitView
      attributionPosition="bottom-left"
    >
      <Controls />
    </ReactFlow>
  );
};

export default CustomNodeFlow;
