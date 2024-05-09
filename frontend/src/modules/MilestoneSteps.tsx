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
  Panel,
  useReactFlow,
  ReactFlowInstance,
  Background,
} from "reactflow";
import "reactflow/dist/style.css";

import videoPlayNode from "../components/videoPlayNode";
import { useSelector } from "react-redux";
import { RootState } from "../store";
import lodash from "lodash";
import { PlusOutlined, SaveOutlined, UploadOutlined } from "@ant-design/icons";
import {
  IndividualStep,
  NodeDataParams,
  RecipeStepDescription,
  VideoState,
} from "../types/InfoTypes";
import { Button, Dropdown, MenuProps, Space } from "antd";
import { milestoneBgColor } from "../looks/coloring";
import FileUploader from "../components/fileUploader";

const nodeTypes = {
  selectorNode: videoPlayNode,
};

const defaultViewport = { x: 0, y: 0, zoom: 0.8 };

const MilestoneInterface = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const edgeUpdateSuccessful = useRef(true);
  const [rfInstance, setRfInstance] = useState<ReactFlowInstance>();

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
            description: val.data.description,
            time: val.videoTime,
            stage: cookingStageName,
            node_id: val.id,
            deleteNode: onDelete,
            updateNode: setNodes,
          } as NodeDataParams,
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

      return { newNodes, newEdges };
    };

    let prepConfig = initNodeInterface(cookingPrep, "Preparation", 10);
    let cookConfig = initNodeInterface(cookingCook, "Cooking", 300);
    let assembleConfig = initNodeInterface(cookingAssemble, "Assembly", 600);

    setNodes([
      ...nodes,
      ...prepConfig.newNodes,
      ...cookConfig.newNodes,
      ...assembleConfig.newNodes,
    ]);
    setEdges((prevEdges) => {
      const uniqueEdges = [
        ...prevEdges,
        ...prepConfig.newEdges.filter(
          (newEdge) => !prevEdges.some((edge) => edge.id === newEdge.id)
        ),
        ...cookConfig.newEdges.filter(
          (newEdge) => !prevEdges.some((edge) => edge.id === newEdge.id)
        ),
        ...assembleConfig.newEdges.filter(
          (newEdge) => !prevEdges.some((edge) => edge.id === newEdge.id)
        ),
      ];
      return uniqueEdges;
    });
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

  const onDelete = useCallback(
    (id: string) => {
      setNodes((nodes) => nodes.filter((node) => node.id !== id));
      setEdges((edges) => edges.filter((edge) => edge.source !== id));
    },
    [setNodes, setEdges]
  );

  const onAdd = useCallback(
    (e: any) => {
      const definedStage: string = e.key as string;
      const posConfig: { [key: string]: { x: number; y: number } } = {
        Preparation: {
          x: 150,
          y: 150,
        },
        Cooking: {
          x: 150,
          y: 450,
        },
        Assembly: {
          x: 150,
          y: 750,
        },
      };
      // get current timestamp
      const timestamp = Date.now();
      const newNode = {
        id: "userNode_" + timestamp.toString(),
        type: "selectorNode",
        data: {
          description: "",
          time: {
            startTime: 0,
            duration: 0,
          } as VideoState,
          stage: definedStage,
          node_id: "userNode_" + timestamp.toString(),
          deleteNode: onDelete,
          updateNode: setNodes,
        } as NodeDataParams,
        position: posConfig[definedStage],
        isConnectable: true,
        // parentNode: "group_prep",
        // extent: "parent",
        dragHandle: ".custom-drag-handle",
      };
      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes]
  );

  const onSave = useCallback(() => {
    if (rfInstance) {
      const flow = rfInstance.toObject();
      let stringFlow = JSON.stringify(flow);
      const blob = new Blob([stringFlow], { type: "application/json" });
      const url = URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = "data.json";
      link.click();

      URL.revokeObjectURL(url);
    }
  }, [rfInstance]);

  const handleFileUpload = (file: File) => {
    const config = file as unknown as {
      nodes: [];
      edges: [];
    }
    setNodes(config.nodes);
    setEdges(config.edges)
  };

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
      onInit={setRfInstance}
      nodeTypes={nodeTypes}
      // connectionLineStyle={connectionLineStyle}
      snapToGrid={true}
      snapGrid={[10, 10]}
      defaultViewport={defaultViewport}
      // fitView
      attributionPosition="bottom-left"
    >
      <Controls />
      <Panel position="top-right">
        <Space direction="horizontal">
          <Dropdown
            menu={{
              items: [
                {
                  key: "Preparation",
                  label: "Preparation",
                },
                {
                  key: "Cooking",
                  label: "Cooking",
                },
                {
                  key: "Assembly",
                  label: "Assembly",
                },
              ] as MenuProps["items"],
              onClick: onAdd,
            }}
          >
            <Button shape="circle" icon={<PlusOutlined />} />
          </Dropdown>
          <FileUploader onFileUpload={handleFileUpload} />
          <Button shape="circle" onClick={onSave}>
            <SaveOutlined />
          </Button>
        </Space>
      </Panel>
      <Background />
      <MiniMap
        zoomable
        pannable
        nodeColor={(n) => milestoneBgColor[n.data.stage]}
        position="bottom-right"
      />
    </ReactFlow>
  );
};

export default MilestoneInterface;
