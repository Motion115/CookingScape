import React, {
  useState,
  useEffect,
  useCallback,
  useRef,
  useMemo,
} from "react";
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
  ConnectionLineType,
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
import { getConfig } from "@testing-library/react";

function capitalizeFirstLetter(word: string): string {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

const defaultViewport = { x: 0, y: 0, zoom: 0.8 };

const MilestoneInterfaceSeq = () => {
  const nodeTypes = useMemo(
    () => ({
      selectorNode: videoPlayNode,
    }),
    []
  );
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const edgeUpdateSuccessful = useRef(true);
  const [rfInstance, setRfInstance] = useState<ReactFlowInstance>();

  const configData = useSelector((state: RootState) => state.setData);
  const cookingPrep = configData.steps.preparation;
  const cookingCook = configData.steps.cooking;
  const cookingAssemble = configData.steps.assembly;
  const cookingSeq = configData.steps.sequential;
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
            id: key,
            data: val,
            videoTime: clipRecord[0],
          };
        }
      );

      let newNodes: any[] = stageStepList.map((val: any, id: number) => {
        let { posX, posY } = { posX: id % 3, posY: Math.floor(id / 3) };
        return {
          id: val.id,
          type: "selectorNode",
          data: {
            description: val.data.description,
            time: val.videoTime,
            stage: capitalizeFirstLetter(val.data.category),
            node_id: val.id,
            time_stamp: Date.now().toString(),
            deleteNode: onDelete,
            updateNode: setNodes,
          } as NodeDataParams,
          position: { x: 25 + posX * 450, y: posY * 240 },
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
        type: ConnectionLineType.Step,
      }));

      return { newNodes, newEdges };
    };

    let seqConfig = initNodeInterface(cookingSeq, "Sequential", 10);

    let prepConfig = initNodeInterface(cookingPrep, "Preparation", 10);
    let cookConfig = initNodeInterface(cookingCook, "Cooking", 300);
    let assembleConfig = initNodeInterface(cookingAssemble, "Assembly", 600);

    setNodes([...nodes, ...seqConfig.newNodes]);
    setEdges((prevEdges) => {
      const uniqueEdges = [
        ...prevEdges,
        ...seqConfig.newEdges.filter(
          (newEdge) => !prevEdges.some((edge) => edge.id === newEdge.id)
        ),
      ];
      return uniqueEdges;
    });
  }, [cookingSeq]);

  const onConnect = useCallback(
    (params: Edge | Connection) =>
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            markerEnd: {
              type: MarkerType.ArrowClosed,
            },
            type: ConnectionLineType.Step,
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
          time_stamp: timestamp.toString(),
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

  const handleFileUpload = useCallback((file: File) => {
    let config = file as unknown as {
      nodes: any[];
      edges: any[];
    };
    config.nodes = config.nodes.map((node: any) => {
      node.data = {
        ...node.data,
        deleteNode: onDelete,
        updateNode: setNodes,
      }
      return node
    })
    setNodes(config.nodes);
    setEdges(config.edges);
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

export default MilestoneInterfaceSeq;
