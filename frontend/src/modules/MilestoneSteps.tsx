import React, { useState, useEffect, useCallback, useRef } from "react";
import ReactFlow, {
  useNodesState,
  useEdgesState,
  addEdge,
  MiniMap,
  Controls,
  Position,
  MarkerType,
  updateEdge,
  Edge,
  Connection,
} from "reactflow";
import "reactflow/dist/style.css";

import videoPlayNode from "../components/videoPlayNode";
import { useSelector } from "react-redux";
import { RootState } from "../store";
import lodash from "lodash";
import { IndividualStep, RecipeStepDescription } from "../types/InfoTypes";

const nodeTypes = {
  selectorNode: videoPlayNode,
};

const defaultViewport = { x: 0, y: 0, zoom: 1.5 };

const MilestoneInterface = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const edgeUpdateSuccessful = useRef(true);

  const configData = useSelector((state: RootState) => state.setData);
  const cookingPrep = configData.steps.preparation;
  const cookingCook = configData.steps.cooking;
  const cookingAssemble = configData.steps.assembly;
  const sceneList = configData.sceneList;

  useEffect(() => {
    const initNodeInterface = (
      cookingStageData: IndividualStep,
      cookingStageName: string,
      baseYpos: number = 0
    ) => {
      let stageStepList = lodash.map(
        cookingStageData,
        (val: RecipeStepDescription, key: string) => {
          let clipRecord = val.clip_id.slice(0, 1).map((val: number) => {
            return sceneList[val.toString()];
          });
          return {
            id: cookingStageName + "_" + key,
            data: val,
            videoTime: clipRecord[0],
          };
        }
      );

      let newNodes: any[] = stageStepList.map((val: any, id: number) => {
        return {
          id: val.id,
          type: "selectorNode",
          data: {
            data: val.data,
            time: val.videoTime,
            stage: cookingStageName,
          },
          position: { x: 25 + id * 450, y: baseYpos },
          isConnectable: true,
          // parentNode: "group_prep",
          // extent: "parent",
          dragHandle: ".custom-drag-handle",
        };
      });

      let newEdges: any[] = stageStepList.slice(0, -1).map((item, i) => ({
        id: item.id + "_" + stageStepList[i + 1].id,
        source: item.id,
        target: stageStepList[i + 1].id,
        updatable: "target",
        markerEnd: {
          type: MarkerType.ArrowClosed,
        },
      }));

      return { newNodes, newEdges }

      
    };

    let prepConfig = initNodeInterface(cookingPrep, "Preparation", 10);
    let cookConfig = initNodeInterface(cookingCook, "Cooking", 300);
    let assembleConfig = initNodeInterface(cookingAssemble, "Assembly", 600);
    setEdges([...edges, ...prepConfig.newEdges, ...cookConfig.newEdges, ...assembleConfig.newEdges]);
    setNodes([...nodes, ...prepConfig.newNodes, ...cookConfig.newNodes, ...assembleConfig.newNodes]);
  }, [cookingPrep, cookingAssemble, cookingCook]);

  const onConnect = useCallback(
    (params: Edge | Connection) =>
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            markerEnd: {
              type: MarkerType.ArrowClosed,
            },
          },
          eds
        )
      ),
    []
  );

  const onEdgeUpdate = useCallback(
    (oldEdge: Edge, newConnection: Connection) => {
      edgeUpdateSuccessful.current = true;
      setEdges((els) => updateEdge(oldEdge, newConnection, els));
    },
    []
  );

  const onEdgeUpdateEnd = useCallback((_: any, edge: Edge) => {
    if (!edgeUpdateSuccessful.current) {
      setEdges((eds) => eds.filter((e) => e.id !== edge.id));
    }
    edgeUpdateSuccessful.current = true;
  }, []);

  const onEdgeUpdateStart = useCallback(() => {
    edgeUpdateSuccessful.current = false;
  }, []);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      onEdgeUpdate={onEdgeUpdate}
      onEdgeUpdateStart={onEdgeUpdateStart}
      onEdgeUpdateEnd={onEdgeUpdateEnd}
      nodeTypes={nodeTypes}
      // connectionLineStyle={connectionLineStyle}
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

export default MilestoneInterface;
