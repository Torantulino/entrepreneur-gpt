import { Connection } from "@xyflow/react";
import { Graph, Block, Node, BlockUIType, Link } from "./types";

/** Creates a copy of the graph with all secrets removed */
export function safeCopyGraph(graph: Graph, block_defs: Block[]): Graph {
  graph = removeAgentInputBlockValues(graph, block_defs);
  return {
    ...graph,
    nodes: graph.nodes.map((node) => {
      const block = block_defs.find((b) => b.id == node.block_id)!;
      return {
        ...node,
        input_default: Object.keys(node.input_default)
          .filter((k) => !block.inputSchema.properties[k].secret)
          .reduce((obj: Node["input_default"], key) => {
            obj[key] = node.input_default[key];
            return obj;
          }, {}),
      };
    }),
  };
}

export function removeAgentInputBlockValues(graph: Graph, blocks: Block[]) {
  const inputBlocks = graph.nodes.filter(
    (node) =>
      blocks.find((b) => b.id === node.block_id)?.uiType === BlockUIType.INPUT,
  );

  const modifiedNodes = graph.nodes.map((node) => {
    if (inputBlocks.find((inputNode) => inputNode.id === node.id)) {
      return {
        ...node,
        input_default: {
          ...node.input_default,
          value: "",
        },
      };
    }
    return node;
  });

  return {
    ...graph,
    nodes: modifiedNodes,
  };
}

export function formatEdgeID(conn: Link | Connection): string {
  if ("sink_id" in conn) {
    return `${conn.source_id}_${conn.source_name}_${conn.sink_id}_${conn.sink_name}`;
  } else {
    return `${conn.source}_${conn.sourceHandle}_${conn.target}_${conn.targetHandle}`;
  }
}
