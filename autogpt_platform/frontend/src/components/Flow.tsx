"use client";
import React, {
  useState,
  useCallback,
  useEffect,
  useRef,
  MouseEvent,
  createContext,
} from "react";
import {
  ReactFlow,
  ReactFlowProvider,
  Controls,
  Background,
  Node,
  OnConnect,
  Connection,
  MarkerType,
  NodeChange,
  EdgeChange,
  useReactFlow,
  applyEdgeChanges,
  applyNodeChanges,
  useViewport,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { CustomNode } from "./CustomNode";
import "./flow.css";
import { BlockUIType, formatEdgeID } from "@/lib/autogpt-server-api";
import { getTypeColor, findNewlyAddedBlockCoordinates } from "@/lib/utils";
import { history } from "./history";
import { CustomEdge } from "./CustomEdge";
import ConnectionLine from "./ConnectionLine";
import { Control, ControlPanel } from "@/components/edit/control/ControlPanel";
import { SaveControl } from "@/components/edit/control/SaveControl";
import { BlocksControl } from "@/components/edit/control/BlocksControl";
import { IconUndo2, IconRedo2 } from "@/components/ui/icons";
import { startTutorial } from "./tutorial";
import useAgentGraph from "@/hooks/useAgentGraph";
import { v4 as uuidv4 } from "uuid";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import RunnerUIWrapper, {
  RunnerUIWrapperRef,
} from "@/components/RunnerUIWrapper";
import PrimaryActionBar from "@/components/PrimaryActionButton";
import { useToast } from "@/components/ui/use-toast";
import { useCopyPaste } from "../hooks/useCopyPaste";
import { CronScheduler } from "./cronScheduler";

// This is for the history, this is the minimum distance a block must move before it is logged
// It helps to prevent spamming the history with small movements especially when pressing on a input in a block
const MINIMUM_MOVE_BEFORE_LOG = 50;

type FlowContextType = {
  visualizeBeads: "no" | "static" | "animate";
  setIsAnyModalOpen: (isOpen: boolean) => void;
  getNextNodeId: () => string;
};

export type NodeDimension = {
  [nodeId: string]: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
};

export const FlowContext = createContext<FlowContextType | null>(null);

const FlowEditor: React.FC<{
  flowID?: string;
  flowVersion?: string;
  className?: string;
}> = ({ flowID, flowVersion, className }) => {
  const {
    addNodes,
    addEdges,
    getNode,
    deleteElements,
    updateNode,
    setViewport,
  } = useReactFlow<CustomNode, CustomEdge>();
  const [nodeId, setNodeId] = useState<number>(1);
  const [isAnyModalOpen, setIsAnyModalOpen] = useState(false);
  const [visualizeBeads, setVisualizeBeads] = useState<
    "no" | "static" | "animate"
  >("animate");
  const [flowExecutionID, setFlowExecutionID] = useState<string | undefined>();
  const {
    agentName,
    setAgentName,
    agentDescription,
    setAgentDescription,
    savedAgent,
    availableNodes,
    availableFlows,
    getOutputType,
    requestSave,
    requestSaveAndRun,
    requestStopRun,
    scheduleRunner,
    isSaving,
    isRunning,
    isStopping,
    isScheduling,
    setIsScheduling,
    nodes,
    setNodes,
    edges,
    setEdges,
  } = useAgentGraph(
    flowID,
    flowVersion ? parseInt(flowVersion) : undefined,
    flowExecutionID,
    visualizeBeads !== "no",
  );

  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();
  const initialPositionRef = useRef<{
    [key: string]: { x: number; y: number };
  }>({});
  const isDragging = useRef(false);

  // State to control if blocks menu should be pinned open
  const [pinBlocksPopover, setPinBlocksPopover] = useState(false);
  // State to control if save popover should be pinned open
  const [pinSavePopover, setPinSavePopover] = useState(false);

  const runnerUIRef = useRef<RunnerUIWrapperRef>(null);

  const [openCron, setOpenCron] = useState(false);

  const { toast } = useToast();

  const TUTORIAL_STORAGE_KEY = "shepherd-tour";

  // It stores the dimension of all nodes with position as well
  const [nodeDimensions, setNodeDimensions] = useState<NodeDimension>({});

  useEffect(() => {
    if (params.get("resetTutorial") === "true") {
      localStorage.removeItem(TUTORIAL_STORAGE_KEY);
      router.push(pathname);
    } else if (!localStorage.getItem(TUTORIAL_STORAGE_KEY)) {
      const emptyNodes = (forceRemove: boolean = false) =>
        forceRemove ? (setNodes([]), setEdges([]), true) : nodes.length === 0;
      startTutorial(emptyNodes, setPinBlocksPopover, setPinSavePopover);
      localStorage.setItem(TUTORIAL_STORAGE_KEY, "yes");
    }
  }, [
    availableNodes,
    router,
    pathname,
    params,
    setEdges,
    setNodes,
    nodes.length,
  ]);

  useEffect(() => {
    if (params.get("open_scheduling") === "true") {
      setOpenCron(true);
    }
    setFlowExecutionID(params.get("flowExecutionID") || undefined);
  }, [params]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().indexOf("MAC") >= 0;
      const isUndo =
        (isMac ? event.metaKey : event.ctrlKey) && event.key === "z";
      const isRedo =
        (isMac ? event.metaKey : event.ctrlKey) &&
        (event.key === "y" || (event.shiftKey && event.key === "Z"));

      if (isUndo) {
        event.preventDefault();
        handleUndo();
      }

      if (isRedo) {
        event.preventDefault();
        handleRedo();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  const onNodeDragStart = (_: MouseEvent, node: Node) => {
    initialPositionRef.current[node.id] = { ...node.position };
    isDragging.current = true;
  };

  const onNodeDragEnd = (_: MouseEvent, node: Node | null) => {
    if (!node) return;

    isDragging.current = false;
    const oldPosition = initialPositionRef.current[node.id];
    const newPosition = node.position;

    // Calculate the movement distance
    if (!oldPosition || !newPosition) return;

    const distanceMoved = Math.sqrt(
      Math.pow(newPosition.x - oldPosition.x, 2) +
        Math.pow(newPosition.y - oldPosition.y, 2),
    );

    if (distanceMoved > MINIMUM_MOVE_BEFORE_LOG) {
      // Minimum movement threshold
      history.push({
        type: "UPDATE_NODE_POSITION",
        payload: { nodeId: node.id, oldPosition, newPosition },
        undo: () => updateNode(node.id, { position: oldPosition }),
        redo: () => updateNode(node.id, { position: newPosition }),
      });
    }
    delete initialPositionRef.current[node.id];
  };

  // Function to clear status, output, and close the output info dropdown of all nodes
  // and reset data beads on edges
  const clearNodesStatusAndOutput = useCallback(() => {
    setNodes((nds) => {
      const newNodes = nds.map((node) => ({
        ...node,
        data: {
          ...node.data,
          status: undefined,
          isOutputOpen: false,
        },
      }));

      return newNodes;
    });
  }, [setNodes]);

  const onNodesChange = useCallback(
    (nodeChanges: NodeChange<CustomNode>[]) => {
      // Persist the changes
      setNodes((prev) => applyNodeChanges(nodeChanges, prev));

      // Remove all edges that were connected to deleted nodes
      nodeChanges
        .filter((change) => change.type === "remove")
        .forEach((deletedNode) => {
          const nodeID = deletedNode.id;
          const deletedNodeData = nodes.find((node) => node.id === nodeID);

          if (deletedNodeData) {
            history.push({
              type: "DELETE_NODE",
              payload: { node: deletedNodeData.data },
              undo: () => addNodes(deletedNodeData),
              redo: () => deleteElements({ nodes: [{ id: nodeID }] }),
            });
          }

          const connectedEdges = edges.filter((edge) =>
            [edge.source, edge.target].includes(nodeID),
          );
          deleteElements({
            edges: connectedEdges.map((edge) => ({ id: edge.id })),
          });
        });
    },
    [deleteElements, setNodes, nodes, edges, addNodes],
  );

  const onConnect: OnConnect = useCallback(
    (connection: Connection) => {
      // Check if this exact connection already exists
      const existingConnection = edges.find(
        (edge) =>
          edge.source === connection.source &&
          edge.target === connection.target &&
          edge.sourceHandle === connection.sourceHandle &&
          edge.targetHandle === connection.targetHandle,
      );

      if (existingConnection) {
        console.warn("This exact connection already exists.");
        return;
      }

      const edgeColor = getTypeColor(
        getOutputType(nodes, connection.source!, connection.sourceHandle!),
      );
      const sourceNode = getNode(connection.source!);
      const newEdge: CustomEdge = {
        id: formatEdgeID(connection),
        type: "custom",
        markerEnd: {
          type: MarkerType.ArrowClosed,
          strokeWidth: 2,
          color: edgeColor,
        },
        data: {
          edgeColor,
          sourcePos: sourceNode!.position,
          isStatic: sourceNode!.data.isOutputStatic,
        },
        ...connection,
        source: connection.source!,
        target: connection.target!,
      };

      addEdges(newEdge);
      history.push({
        type: "ADD_EDGE",
        payload: { edge: newEdge },
        undo: () => {
          deleteElements({ edges: [{ id: newEdge.id }] });
        },
        redo: () => {
          addEdges(newEdge);
        },
      });
      clearNodesStatusAndOutput(); // Clear status and output on connection change
    },
    [
      getNode,
      addEdges,
      deleteElements,
      clearNodesStatusAndOutput,
      nodes,
      edges,
      formatEdgeID,
      getOutputType,
    ],
  );

  const onEdgesChange = useCallback(
    (edgeChanges: EdgeChange<CustomEdge>[]) => {
      // Persist the changes
      setEdges((prev) => applyEdgeChanges(edgeChanges, prev));

      // Propagate edge changes to node data
      const addedEdges = edgeChanges.filter((change) => change.type === "add"),
        replaceEdges = edgeChanges.filter(
          (change) => change.type === "replace",
        ),
        removedEdges = edgeChanges.filter((change) => change.type === "remove"),
        selectedEdges = edgeChanges.filter(
          (change) => change.type === "select",
        );

      if (addedEdges.length > 0 || removedEdges.length > 0) {
        setNodes((nds) => {
          const newNodes = nds.map((node) => ({
            ...node,
            data: {
              ...node.data,
              connections: [
                // Remove node connections for deleted edges
                ...node.data.connections.filter(
                  (conn) =>
                    !removedEdges.some(
                      (removedEdge) => removedEdge.id === conn.edge_id,
                    ),
                ),
                // Add node connections for added edges
                ...addedEdges.map((addedEdge) => ({
                  edge_id: addedEdge.item.id,
                  source: addedEdge.item.source,
                  target: addedEdge.item.target,
                  sourceHandle: addedEdge.item.sourceHandle!,
                  targetHandle: addedEdge.item.targetHandle!,
                })),
              ],
            },
          }));

          return newNodes;
        });

        if (removedEdges.length > 0) {
          clearNodesStatusAndOutput(); // Clear status and output on edge deletion
        }
      }

      if (replaceEdges.length > 0) {
        // Reset node connections for all edges
        console.warn(
          "useReactFlow().setRootEdges was used to overwrite all edges. " +
            "Use addEdges, deleteElements, or reconnectEdge for incremental changes.",
          replaceEdges,
        );
        setNodes((nds) =>
          nds.map((node) => ({
            ...node,
            data: {
              ...node.data,
              connections: [
                ...replaceEdges.map((replaceEdge) => ({
                  edge_id: replaceEdge.item.id,
                  source: replaceEdge.item.source,
                  target: replaceEdge.item.target,
                  sourceHandle: replaceEdge.item.sourceHandle!,
                  targetHandle: replaceEdge.item.targetHandle!,
                })),
              ],
            },
          })),
        );
        clearNodesStatusAndOutput();
      }
    },
    [setNodes, clearNodesStatusAndOutput, setEdges],
  );

  const getNextNodeId = useCallback(() => {
    return uuidv4();
  }, []);

  const { x, y, zoom } = useViewport();

  // Set the initial view port to center the canvas.
  useEffect(() => {
    if (nodes.length <= 0 || x !== 0 || y !== 0) {
      return;
    }

    const topLeft = { x: Infinity, y: Infinity };
    const bottomRight = { x: -Infinity, y: -Infinity };

    nodes.forEach((node) => {
      const { x, y } = node.position;
      topLeft.x = Math.min(topLeft.x, x);
      topLeft.y = Math.min(topLeft.y, y);
      // Rough estimate of the width and height of the node: 500x400.
      bottomRight.x = Math.max(bottomRight.x, x + 500);
      bottomRight.y = Math.max(bottomRight.y, y + 400);
    });

    const centerX = (topLeft.x + bottomRight.x) / 2;
    const centerY = (topLeft.y + bottomRight.y) / 2;
    const zoom = 0.8;

    setViewport({
      x: window.innerWidth / 2 - centerX * zoom,
      y: window.innerHeight / 2 - centerY * zoom,
      zoom: zoom,
    });
  }, [nodes, setViewport, x, y]);

  const addNode = useCallback(
    (blockId: string, nodeType: string, hardcodedValues: any = {}) => {
      const nodeSchema = availableNodes.find((node) => node.id === blockId);
      if (!nodeSchema) {
        console.error(`Schema not found for block ID: ${blockId}`);
        return;
      }

      /*
       Calculate a position to the right of the newly added block, allowing for some margin.
       If adding to the right side causes the new block to collide with an existing block, attempt to place it at the bottom or left.
       Why not the top? Because the height of the new block is unknown.
       If it still collides, run a loop to find the best position where it does not collide.
       Then, adjust the canvas to center on the newly added block.
       Note: The width is known, e.g., w = 300px for a note and w = 500px for others, but the height is dynamic.
       */

      // Alternative: We could also use D3 force, Intersection for this (React flow Pro examples)

      const viewportCoordinates =
        nodeDimensions && Object.keys(nodeDimensions).length > 0
          ? // we will get all the dimension of nodes, then store
            findNewlyAddedBlockCoordinates(
              nodeDimensions,
              nodeSchema.uiType == BlockUIType.NOTE ? 300 : 500,
              60,
              1.0,
            )
          : // we will get all the dimension of nodes, then store
            {
              x: window.innerWidth / 2 - x,
              y: window.innerHeight / 2 - y,
            };

      const newNode: CustomNode = {
        id: nodeId.toString(),
        type: "custom",
        position: viewportCoordinates, // Set the position to the calculated viewport center
        data: {
          blockType: nodeType,
          blockCosts: nodeSchema.costs,
          title: `${nodeType} ${nodeId}`,
          description: nodeSchema.description,
          categories: nodeSchema.categories,
          inputSchema: nodeSchema.inputSchema,
          outputSchema: nodeSchema.outputSchema,
          hardcodedValues: hardcodedValues,
          connections: [],
          isOutputOpen: false,
          block_id: blockId,
          isOutputStatic: nodeSchema.staticOutput,
          uiType: nodeSchema.uiType,
        },
      };

      addNodes(newNode);
      setNodeId((prevId) => prevId + 1);
      clearNodesStatusAndOutput(); // Clear status and output when a new node is added

      setViewport(
        {
          // Rough estimate of the dimension of the node is: 500x400px.
          // Though we skip shifting the X, considering the block menu side-bar.
          x: -viewportCoordinates.x * 0.8 + (window.innerWidth - 0.0) / 2,
          y: -viewportCoordinates.y * 0.8 + (window.innerHeight - 400) / 2,
          zoom: 0.8,
        },
        { duration: 500 },
      );

      history.push({
        type: "ADD_NODE",
        payload: { node: { ...newNode, ...newNode.data } },
        undo: () => deleteElements({ nodes: [{ id: newNode.id }] }),
        redo: () => addNodes(newNode),
      });
    },
    [
      nodeId,
      setViewport,
      availableNodes,
      addNodes,
      nodeDimensions,
      deleteElements,
      clearNodesStatusAndOutput,
      x,
      y,
    ],
  );

  const findNodeDimensions = useCallback(() => {
    const newNodeDimensions: NodeDimension = nodes.reduce((acc, node) => {
      const nodeElement = document.querySelector(
        `[data-id="custom-node-${node.id}"]`,
      );
      if (nodeElement) {
        const rect = nodeElement.getBoundingClientRect();
        const { left, top, width, height } = rect;

        // Convert screen coordinates to flow coordinates
        const flowX = (left - x) / zoom;
        const flowY = (top - y) / zoom;
        const flowWidth = width / zoom;
        const flowHeight = height / zoom;

        acc[node.id] = {
          x: flowX,
          y: flowY,
          width: flowWidth,
          height: flowHeight,
        };
      }
      return acc;
    }, {} as NodeDimension);

    setNodeDimensions(newNodeDimensions);
  }, [nodes, x, y, zoom]);

  useEffect(() => {
    findNodeDimensions();
  }, [nodes, findNodeDimensions]);

  const handleUndo = () => {
    history.undo();
  };

  const handleRedo = () => {
    history.redo();
  };

  const handleCopyPaste = useCopyPaste(getNextNodeId);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Prevent copy/paste if any modal is open or if the focus is on an input element
      const activeElement = document.activeElement;
      const isInputField =
        activeElement?.tagName === "INPUT" ||
        activeElement?.tagName === "TEXTAREA" ||
        activeElement?.getAttribute("contenteditable") === "true";

      if (isAnyModalOpen || isInputField) return;

      handleCopyPaste(event);
    },
    [isAnyModalOpen, handleCopyPaste],
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleKeyDown]);

  const onNodesDelete = useCallback(() => {
    clearNodesStatusAndOutput();
  }, [clearNodesStatusAndOutput]);

  const editorControls: Control[] = [
    {
      label: "Undo",
      icon: <IconUndo2 />,
      onClick: handleUndo,
    },
    {
      label: "Redo",
      icon: <IconRedo2 />,
      onClick: handleRedo,
    },
  ];

  // This function is called after cron expression is created
  // So you can collect inputs for scheduling
  const afterCronCreation = (cronExpression: string) => {
    runnerUIRef.current?.collectInputsForScheduling(cronExpression);
  };

  // This function Opens up form for creating cron expression
  const handleScheduleButton = () => {
    if (!savedAgent) {
      toast({
        title: `Please save the agent using the button in the left sidebar before running it.`,
        duration: 2000,
      });
      return;
    }
    setOpenCron(true);
  };

  return (
    <FlowContext.Provider
      value={{ visualizeBeads, setIsAnyModalOpen, getNextNodeId }}
    >
      <div className={className}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={{ custom: CustomNode }}
          edgeTypes={{ custom: CustomEdge }}
          connectionLineComponent={ConnectionLine}
          onConnect={onConnect}
          onNodesChange={onNodesChange}
          onNodesDelete={onNodesDelete}
          onEdgesChange={onEdgesChange}
          onNodeDragStop={onNodeDragEnd}
          onNodeDragStart={onNodeDragStart}
          deleteKeyCode={["Backspace", "Delete"]}
          minZoom={0.1}
          maxZoom={2}
          className="dark:bg-slate-900"
        >
          <Controls />
          <Background className="dark:bg-slate-800" />
          <ControlPanel
            className="absolute z-10"
            controls={editorControls}
            topChildren={
              <BlocksControl
                pinBlocksPopover={pinBlocksPopover} // Pass the state to BlocksControl
                blocks={availableNodes}
                addBlock={addNode}
                flows={availableFlows}
                nodes={nodes}
              />
            }
            botChildren={
              <SaveControl
                agentMeta={savedAgent}
                canSave={!isSaving && !isRunning && !isStopping}
                onSave={() => requestSave()}
                agentDescription={agentDescription}
                onDescriptionChange={setAgentDescription}
                agentName={agentName}
                onNameChange={setAgentName}
                pinSavePopover={pinSavePopover}
              />
            }
          ></ControlPanel>
          <PrimaryActionBar
            onClickAgentOutputs={() => runnerUIRef.current?.openRunnerOutput()}
            onClickRunAgent={() => {
              if (!savedAgent) {
                toast({
                  title: `Please save the agent using the button in the left sidebar before running it.`,
                  duration: 2000,
                });
                return;
              }
              if (!isRunning) {
                runnerUIRef.current?.runOrOpenInput();
              } else {
                requestStopRun();
              }
            }}
            onClickScheduleButton={handleScheduleButton}
            isScheduling={isScheduling}
            isDisabled={!savedAgent}
            isRunning={isRunning}
            requestStopRun={requestStopRun}
            runAgentTooltip={!isRunning ? "Run Agent" : "Stop Agent"}
          />
          <CronScheduler
            afterCronCreation={afterCronCreation}
            open={openCron}
            setOpen={setOpenCron}
          />
        </ReactFlow>
      </div>
      <RunnerUIWrapper
        ref={runnerUIRef}
        nodes={nodes}
        setNodes={setNodes}
        setIsScheduling={setIsScheduling}
        isScheduling={isScheduling}
        isRunning={isRunning}
        scheduleRunner={scheduleRunner}
        requestSaveAndRun={requestSaveAndRun}
      />
    </FlowContext.Provider>
  );
};

const WrappedFlowEditor: typeof FlowEditor = (props) => (
  <ReactFlowProvider>
    <FlowEditor {...props} />
  </ReactFlowProvider>
);

export default WrappedFlowEditor;
