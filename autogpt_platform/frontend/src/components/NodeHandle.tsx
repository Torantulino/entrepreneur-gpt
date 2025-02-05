import { BlockIOSubSchema } from "@/lib/autogpt-server-api/types";
import { beautifyString, getTypeBgColor, getTypeTextColor } from "@/lib/utils";
import { FC } from "react";
import { Handle, Position } from "@xyflow/react";
import SchemaTooltip from "./SchemaTooltip";

type HandleProps = {
  keyName: string;
  schema: BlockIOSubSchema;
  isConnected: boolean;
  isRequired?: boolean;
  side: "left" | "right";
  title?: string;
};

const NodeHandle: FC<HandleProps> = ({
  keyName,
  schema,
  isConnected,
  isRequired,
  side,
  title,
}) => {
  const typeName: Record<string, string> = {
    string: "text",
    number: "number",
    integer: "integer",
    boolean: "true/false",
    object: "object",
    array: "list",
    null: "null",
  };

  const typeClass = `text-sm ${getTypeTextColor(schema.type || "any")} ${side === "left" ? "text-left" : "text-right"}`;

  const label = (
    <div className="flex grow flex-row">
      <span className="text-m green flex items-end pr-2 text-gray-900 dark:text-gray-100">
        {title || schema.title || beautifyString(keyName.toLowerCase())}
        {isRequired ? "*" : ""}
      </span>
      <span className={`${typeClass} flex items-end`}>
        ({typeName[schema.type as keyof typeof typeName] || "any"})
      </span>
    </div>
  );

  const Dot = () => {
    const color = isConnected
      ? getTypeBgColor(schema.type || "any")
      : "border-gray-300 dark:border-gray-600";
    return (
      <div
        className={`${color} m-1 h-4 w-4 rounded-full border-2 bg-white transition-colors duration-100 group-hover:bg-gray-300 dark:bg-slate-800 dark:group-hover:bg-gray-700`}
      />
    );
  };

  if (side === "left") {
    return (
      <div key={keyName} className="handle-container">
        <Handle
          type="target"
          data-testid={`input-handle-${keyName}`}
          position={Position.Left}
          id={keyName}
          className="group -ml-[38px]"
        >
          <div className="pointer-events-none flex items-center">
            <Dot />
            {label}
          </div>
        </Handle>
        <SchemaTooltip description={schema.description} />
      </div>
    );
  } else {
    return (
      <div key={keyName} className="handle-container justify-end">
        <Handle
          type="source"
          data-testid={`output-handle-${keyName}`}
          position={Position.Right}
          id={keyName}
          className="group -mr-[38px]"
        >
          <div className="pointer-events-none flex items-center">
            {label}
            <Dot />
          </div>
        </Handle>
      </div>
    );
  }
};

export default NodeHandle;
