import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { format } from "date-fns";
import { CalendarIcon, Clock } from "lucide-react";
import { Cross2Icon, Pencil2Icon, PlusIcon } from "@radix-ui/react-icons";
import { beautifyString, cn } from "@/lib/utils";
import {
  BlockIORootSchema,
  BlockIOSubSchema,
  BlockIOObjectSubSchema,
  BlockIOKVSubSchema,
  BlockIOArraySubSchema,
  BlockIOStringSubSchema,
  BlockIONumberSubSchema,
  BlockIOBooleanSubSchema,
  BlockIOSimpleTypeSubSchema,
} from "@/lib/autogpt-server-api/types";
import React, { FC, useCallback, useEffect, useMemo, useState } from "react";
import { Button } from "./ui/button";
import { Switch } from "./ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import {
  MultiSelector,
  MultiSelectorContent,
  MultiSelectorInput,
  MultiSelectorItem,
  MultiSelectorList,
  MultiSelectorTrigger,
} from "./ui/multiselect";
import { LocalValuedInput } from "./ui/input";
import NodeHandle from "./NodeHandle";
import { ConnectionData } from "./CustomNode";
import { CredentialsInput } from "./integrations/credentials-input";

type NodeObjectInputTreeProps = {
  nodeId: string;
  selfKey?: string;
  schema: BlockIORootSchema | BlockIOObjectSubSchema;
  object?: { [key: string]: any };
  connections: ConnectionData;
  handleInputClick: (key: string) => void;
  handleInputChange: (key: string, value: any) => void;
  errors: { [key: string]: string | undefined };
  className?: string;
  displayName?: string;
};

const NodeObjectInputTree: FC<NodeObjectInputTreeProps> = ({
  nodeId,
  selfKey = "",
  schema,
  object,
  connections,
  handleInputClick,
  handleInputChange,
  errors,
  className,
  displayName,
}) => {
  object ||= ("default" in schema ? schema.default : null) ?? {};
  return (
    <div className={cn(className, "w-full flex-col")}>
      {Object.entries(schema.properties).map(([propKey, propSchema]) => {
        const childKey = selfKey ? `${selfKey}.${propKey}` : propKey;

        return (
          <div
            key={propKey}
            className="flex w-full flex-row justify-between space-y-2"
          >
            <span className="mr-2 mt-3 dark:text-gray-300">
              {propSchema.title || beautifyString(propKey)}
            </span>
            <NodeGenericInputField
              nodeId={nodeId}
              key={propKey}
              propKey={childKey}
              propSchema={propSchema}
              currentValue={object ? object[propKey] : undefined}
              errors={errors}
              connections={connections}
              handleInputChange={handleInputChange}
              handleInputClick={handleInputClick}
              displayName={propSchema.title || beautifyString(propKey)}
            />
          </div>
        );
      })}
    </div>
  );
};

export default NodeObjectInputTree;

const NodeImageInput: FC<{
  selfKey: string;
  schema: BlockIOStringSubSchema;
  value?: string;
  error?: string;
  handleInputChange: NodeObjectInputTreeProps["handleInputChange"];
  className?: string;
  displayName: string;
}> = ({
  selfKey,
  schema,
  value = "",
  error,
  handleInputChange,
  className,
  displayName,
}) => {
  const handleFileChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      // Validate file type
      if (!file.type.startsWith("image/")) {
        console.error("Please upload an image file");
        return;
      }

      // Convert to base64
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64String = (e.target?.result as string).split(",")[1];
        handleInputChange(selfKey, base64String);
      };
      reader.readAsDataURL(file);
    },
    [selfKey, handleInputChange],
  );

  return (
    <div className={cn("flex flex-col gap-2", className)}>
      <div className="nodrag flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() =>
              document.getElementById(`${selfKey}-upload`)?.click()
            }
            className="w-full"
          >
            {value ? "Change Image" : `Upload ${displayName}`}
          </Button>
          {value && (
            <Button
              variant="ghost"
              className="text-red-500 hover:text-red-700"
              onClick={() => handleInputChange(selfKey, "")}
            >
              <Cross2Icon className="h-4 w-4" />
            </Button>
          )}
        </div>

        <input
          id={`${selfKey}-upload`}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />

        {value && (
          <div className="relative mt-2 rounded-md border border-gray-300 p-2 dark:border-gray-600">
            <img
              src={`data:image/jpeg;base64,${value}`}
              alt="Preview"
              className="max-h-32 w-full rounded-md object-contain"
            />
          </div>
        )}
      </div>
      {error && <span className="error-message">{error}</span>}
    </div>
  );
};

const NodeDateTimeInput: FC<{
  selfKey: string;
  schema: BlockIOStringSubSchema;
  value?: string;
  error?: string;
  handleInputChange: NodeObjectInputTreeProps["handleInputChange"];
  className?: string;
  displayName: string;
}> = ({
  selfKey,
  schema,
  value = "",
  error,
  handleInputChange,
  className,
  displayName,
}) => {
  const date = value ? new Date(value) : new Date();
  const [timeInput, setTimeInput] = useState(
    value ? format(date, "HH:mm") : "00:00",
  );

  const handleDateSelect = (newDate: Date | undefined) => {
    if (!newDate) return;

    const [hours, minutes] = timeInput.split(":").map(Number);
    newDate.setHours(hours, minutes);
    handleInputChange(selfKey, newDate.toISOString());
  };

  const handleTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = e.target.value;
    setTimeInput(newTime);

    if (value) {
      const [hours, minutes] = newTime.split(":").map(Number);
      const newDate = new Date(value);
      newDate.setHours(hours, minutes);
      handleInputChange(selfKey, newDate.toISOString());
    }
  };

  return (
    <div className={cn("flex flex-col gap-2", className)}>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              "w-full justify-start text-left font-normal",
              !value && "text-muted-foreground",
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {value ? format(date, "PPP") : <span>Pick a date</span>}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={date}
            onSelect={handleDateSelect}
            initialFocus
          />
        </PopoverContent>
      </Popover>
      <LocalValuedInput
        type="time"
        value={timeInput}
        onChange={handleTimeChange}
        className="w-full"
      />
      {error && <span className="error-message">{error}</span>}
    </div>
  );
};

export const NodeGenericInputField: FC<{
  nodeId: string;
  propKey: string;
  propSchema: BlockIOSubSchema;
  currentValue?: any;
  errors: NodeObjectInputTreeProps["errors"];
  connections: NodeObjectInputTreeProps["connections"];
  handleInputChange: NodeObjectInputTreeProps["handleInputChange"];
  handleInputClick: NodeObjectInputTreeProps["handleInputClick"];
  className?: string;
  displayName?: string;
}> = ({
  nodeId,
  propKey,
  propSchema,
  currentValue,
  errors,
  connections,
  handleInputChange,
  handleInputClick,
  className,
  displayName,
}) => {
  className = cn(className);
  displayName ||= propSchema.title || beautifyString(propKey);

  if ("allOf" in propSchema) {
    // If this happens, that is because Pydantic wraps $refs in an allOf if the
    // $ref has sibling schema properties (which isn't technically allowed),
    // so there will only be one item in allOf[].
    // AFAIK this should NEVER happen though, as $refs are resolved server-side.
    propSchema = propSchema.allOf[0];
    console.warn(`Unsupported 'allOf' in schema for '${propKey}'!`, propSchema);
  }

  if ("credentials_provider" in propSchema) {
    return (
      <NodeCredentialsInput
        selfKey={propKey}
        value={currentValue}
        errors={errors}
        className={className}
        handleInputChange={handleInputChange}
      />
    );
  }

  if ("properties" in propSchema) {
    // Render a multi-select for all-boolean sub-schemas with more than 3 properties
    if (
      Object.values(propSchema.properties).every(
        (subSchema) => "type" in subSchema && subSchema.type == "boolean",
      ) &&
      Object.keys(propSchema.properties).length >= 3
    ) {
      const options = Object.keys(propSchema.properties);
      const selectedKeys = Object.entries(currentValue || {})
        .filter(([_, v]) => v)
        .map(([k, _]) => k);
      return (
        <NodeMultiSelectInput
          selfKey={propKey}
          schema={propSchema}
          selection={selectedKeys}
          error={errors[propKey]}
          className={className}
          displayName={displayName}
          handleInputChange={(key, selection) => {
            handleInputChange(
              key,
              Object.fromEntries(
                options.map((option) => [option, selection.includes(option)]),
              ),
            );
          }}
        />
      );
    }

    return (
      <NodeObjectInputTree
        nodeId={nodeId}
        selfKey={propKey}
        schema={propSchema}
        object={currentValue}
        errors={errors}
        className={cn("border-l border-gray-500 pl-2", className)} // visual indent
        displayName={displayName}
        connections={connections}
        handleInputClick={handleInputClick}
        handleInputChange={handleInputChange}
      />
    );
  }

  if ("additionalProperties" in propSchema) {
    return (
      <NodeKeyValueInput
        nodeId={nodeId}
        selfKey={propKey}
        schema={propSchema}
        entries={currentValue}
        errors={errors}
        className={className}
        displayName={displayName}
        connections={connections}
        handleInputChange={handleInputChange}
      />
    );
  }

  if ("anyOf" in propSchema) {
    // Optional oneOf
    if (
      "oneOf" in propSchema.anyOf[0] &&
      propSchema.anyOf[0].oneOf &&
      "discriminator" in propSchema.anyOf[0] &&
      propSchema.anyOf[0].discriminator
    ) {
      return (
        <NodeOneOfDiscriminatorField
          nodeId={nodeId}
          propKey={propKey}
          propSchema={propSchema.anyOf[0]}
          defaultValue={propSchema.default}
          currentValue={currentValue}
          errors={errors}
          connections={connections}
          handleInputChange={handleInputChange}
          handleInputClick={handleInputClick}
          className={className}
          displayName={displayName}
        />
      );
    }

    // optional items
    const types = propSchema.anyOf.map((s) =>
      "type" in s ? s.type : undefined,
    );
    if (types.includes("string") && types.includes("null")) {
      // optional string and datetime

      if (
        "format" in propSchema.anyOf[0] &&
        propSchema.anyOf[0].format === "date-time"
      ) {
        return (
          <NodeDateTimeInput
            selfKey={propKey}
            schema={propSchema.anyOf[0]}
            value={currentValue}
            error={errors[propKey]}
            className={className}
            displayName={displayName}
            handleInputChange={handleInputChange}
          />
        );
      }

      return (
        <NodeStringInput
          selfKey={propKey}
          schema={
            {
              ...propSchema,
              type: "string",
              enum: (propSchema.anyOf[0] as BlockIOStringSubSchema).enum,
            } as BlockIOStringSubSchema
          }
          value={currentValue}
          error={errors[propKey]}
          className={className}
          displayName={displayName}
          handleInputChange={handleInputChange}
          handleInputClick={handleInputClick}
        />
      );
    } else if (
      (types.includes("integer") || types.includes("number")) &&
      types.includes("null")
    ) {
      return (
        <NodeNumberInput
          selfKey={propKey}
          schema={
            {
              ...propSchema,
              type: "integer",
            } as BlockIONumberSubSchema
          }
          value={currentValue}
          error={errors[propKey]}
          className={className}
          displayName={displayName}
          handleInputChange={handleInputChange}
        />
      );
    } else if (types.includes("array") && types.includes("null")) {
      return (
        <NodeArrayInput
          nodeId={nodeId}
          selfKey={propKey}
          schema={
            {
              ...propSchema,
              type: "array",
              items: (propSchema.anyOf[0] as BlockIOArraySubSchema).items,
            } as BlockIOArraySubSchema
          }
          entries={currentValue}
          errors={errors}
          className={className}
          displayName={displayName}
          connections={connections}
          handleInputChange={handleInputChange}
          handleInputClick={handleInputClick}
        />
      );
    } else if (types.includes("object") && types.includes("null")) {
      // rendering optional mutliselect
      if (
        Object.values(
          (propSchema.anyOf[0] as BlockIOObjectSubSchema).properties,
        ).every(
          (subSchema) => "type" in subSchema && subSchema.type == "boolean",
        ) &&
        Object.keys((propSchema.anyOf[0] as BlockIOObjectSubSchema).properties)
          .length >= 1
      ) {
        const options = Object.keys(
          (propSchema.anyOf[0] as BlockIOObjectSubSchema).properties,
        );
        const selectedKeys = Object.entries(currentValue || {})
          .filter(([_, v]) => v)
          .map(([k, _]) => k);
        return (
          <NodeMultiSelectInput
            selfKey={propKey}
            schema={propSchema.anyOf[0] as BlockIOObjectSubSchema}
            selection={selectedKeys}
            error={errors[propKey]}
            className={className}
            displayName={displayName}
            handleInputChange={(key, selection) => {
              handleInputChange(
                key,
                Object.fromEntries(
                  options.map((option) => [option, selection.includes(option)]),
                ),
              );
            }}
          />
        );
      }

      return (
        <NodeKeyValueInput
          nodeId={nodeId}
          selfKey={propKey}
          schema={
            {
              ...propSchema,
              type: "object",
              additionalProperties: (propSchema.anyOf[0] as BlockIOKVSubSchema)
                .additionalProperties,
            } as BlockIOKVSubSchema
          }
          entries={currentValue}
          errors={errors}
          className={className}
          displayName={displayName}
          connections={connections}
          handleInputChange={handleInputChange}
        />
      );
    }
  }

  if (
    "oneOf" in propSchema &&
    propSchema.oneOf &&
    "discriminator" in propSchema &&
    propSchema.discriminator
  ) {
    return (
      <NodeOneOfDiscriminatorField
        nodeId={nodeId}
        propKey={propKey}
        propSchema={propSchema}
        currentValue={currentValue}
        defaultValue={propSchema.default}
        errors={errors}
        connections={connections}
        handleInputChange={handleInputChange}
        handleInputClick={handleInputClick}
        className={className}
        displayName={displayName}
      />
    );
  }

  if (!("type" in propSchema)) {
    return (
      <NodeFallbackInput
        selfKey={propKey}
        schema={propSchema}
        value={currentValue}
        error={errors[propKey]}
        className={className}
        displayName={displayName}
        handleInputChange={handleInputChange}
        handleInputClick={handleInputClick}
      />
    );
  }

  switch (propSchema.type) {
    case "string":
      if ("image_upload" in propSchema && propSchema.image_upload === true) {
        return (
          <NodeImageInput
            selfKey={propKey}
            schema={propSchema}
            value={currentValue}
            error={errors[propKey]}
            className={className}
            displayName={displayName}
            handleInputChange={handleInputChange}
          />
        );
      }
      if ("format" in propSchema && propSchema.format === "date-time") {
        return (
          <NodeDateTimeInput
            selfKey={propKey}
            schema={propSchema}
            value={currentValue}
            error={errors[propKey]}
            className={className}
            displayName={displayName}
            handleInputChange={handleInputChange}
          />
        );
      }
      return (
        <NodeStringInput
          selfKey={propKey}
          schema={propSchema}
          value={currentValue}
          error={errors[propKey]}
          className={className}
          displayName={displayName}
          handleInputChange={handleInputChange}
          handleInputClick={handleInputClick}
        />
      );
    case "boolean":
      return (
        <NodeBooleanInput
          selfKey={propKey}
          schema={propSchema}
          value={currentValue}
          error={errors[propKey]}
          className={className}
          displayName={displayName}
          handleInputChange={handleInputChange}
        />
      );
    case "number":
    case "integer":
      return (
        <NodeNumberInput
          selfKey={propKey}
          schema={propSchema}
          value={currentValue}
          error={errors[propKey]}
          className={className}
          displayName={displayName}
          handleInputChange={handleInputChange}
        />
      );
    case "array":
      return (
        <NodeArrayInput
          nodeId={nodeId}
          selfKey={propKey}
          schema={propSchema}
          entries={currentValue}
          errors={errors}
          className={className}
          displayName={displayName}
          connections={connections}
          handleInputChange={handleInputChange}
          handleInputClick={handleInputClick}
        />
      );
    case "object":
      return (
        <NodeKeyValueInput
          nodeId={nodeId}
          selfKey={propKey}
          schema={propSchema}
          entries={currentValue}
          errors={errors}
          className={className}
          displayName={displayName}
          connections={connections}
          handleInputChange={handleInputChange}
        />
      );
    default:
      console.warn(
        `Schema for '${propKey}' specifies unknown type:`,
        propSchema,
      );
      return (
        <NodeFallbackInput
          selfKey={propKey}
          schema={propSchema}
          value={currentValue}
          error={errors[propKey]}
          className={className}
          displayName={displayName}
          handleInputChange={handleInputChange}
          handleInputClick={handleInputClick}
        />
      );
  }
};

const NodeOneOfDiscriminatorField: FC<{
  nodeId: string;
  propKey: string;
  propSchema: any;
  currentValue?: any;
  defaultValue?: any;
  errors: { [key: string]: string | undefined };
  connections: ConnectionData;
  handleInputChange: (key: string, value: any) => void;
  handleInputClick: (key: string) => void;
  className?: string;
  displayName?: string;
}> = ({
  nodeId,
  propKey,
  propSchema,
  currentValue,
  defaultValue,
  errors,
  connections,
  handleInputChange,
  handleInputClick,
  className,
}) => {
  const discriminator = propSchema.discriminator;
  const discriminatorProperty = discriminator.propertyName;

  const variantOptions = useMemo(() => {
    const oneOfVariants = propSchema.oneOf || [];

    return oneOfVariants
      .map((variant: any) => {
        const variantDiscValue =
          variant.properties?.[discriminatorProperty]?.const;

        return {
          value: variantDiscValue,
          schema: variant as BlockIOSubSchema,
        };
      })
      .filter((v: any) => v.value != null);
  }, [discriminatorProperty, propSchema.oneOf]);

  const initialVariant = defaultValue
    ? variantOptions.find(
        (opt: any) => defaultValue[discriminatorProperty] === opt.value,
      )
    : currentValue
      ? variantOptions.find(
          (opt: any) => currentValue[discriminatorProperty] === opt.value,
        )
      : null;

  const [chosenType, setChosenType] = useState<string>(
    initialVariant?.value || "",
  );

  useEffect(() => {
    if (initialVariant && !currentValue) {
      handleInputChange(
        propKey,
        defaultValue || {
          [discriminatorProperty]: initialVariant.value,
        },
      );
    }
  }, []);

  const handleVariantChange = (newType: string) => {
    setChosenType(newType);
    const chosenVariant = variantOptions.find(
      (opt: any) => opt.value === newType,
    );
    if (chosenVariant) {
      const initialValue = {
        [discriminatorProperty]: newType,
      };
      handleInputChange(propKey, initialValue);
    }
  };

  const chosenVariantSchema = variantOptions.find(
    (opt: any) => opt.value === chosenType,
  )?.schema;

  function getEntryKey(key: string): string {
    // use someKey for handle purpose (not childKey)
    return `${propKey}_#_${key}`;
  }

  function isConnected(key: string): boolean {
    return connections.some(
      (c) => c.targetHandle === getEntryKey(key) && c.target === nodeId,
    );
  }

  return (
    <div
      className={cn(
        "flex min-w-[400px] max-w-[95%] flex-col space-y-4",
        className,
      )}
    >
      <Select value={chosenType || ""} onValueChange={handleVariantChange}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Select a type..." />
        </SelectTrigger>
        <SelectContent>
          {variantOptions.map((opt: any) => (
            <SelectItem key={opt.value} value={opt.value}>
              {beautifyString(opt.value)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {chosenVariantSchema && (
        <div className={cn(className, "w-full flex-col")}>
          {Object.entries(chosenVariantSchema.properties).map(
            ([someKey, childSchema]) => {
              if (someKey === "discriminator") {
                return null;
              }
              const childKey = propKey ? `${propKey}.${someKey}` : someKey; // for history redo/undo purpose
              return (
                <div
                  key={childKey}
                  className="mb-4 flex w-full flex-col justify-between space-y-2"
                >
                  <NodeHandle
                    keyName={getEntryKey(someKey)}
                    schema={childSchema as BlockIOSubSchema}
                    isConnected={isConnected(getEntryKey(someKey))}
                    isRequired={false}
                    side="left"
                  />

                  {!isConnected(someKey) && (
                    <NodeGenericInputField
                      nodeId={nodeId}
                      key={propKey}
                      propKey={childKey}
                      propSchema={childSchema as BlockIOSubSchema}
                      currentValue={
                        currentValue
                          ? currentValue[someKey]
                          : defaultValue?.[someKey]
                      }
                      errors={errors}
                      connections={connections}
                      handleInputChange={handleInputChange}
                      handleInputClick={handleInputClick}
                      displayName={beautifyString(someKey)}
                    />
                  )}
                </div>
              );
            },
          )}
        </div>
      )}
    </div>
  );
};

const NodeCredentialsInput: FC<{
  selfKey: string;
  value: any;
  errors: { [key: string]: string | undefined };
  handleInputChange: NodeObjectInputTreeProps["handleInputChange"];
  className?: string;
}> = ({ selfKey, value, errors, handleInputChange, className }) => {
  return (
    <div className={cn("flex flex-col", className)}>
      <CredentialsInput
        selfKey={selfKey}
        onSelectCredentials={(credsMeta) =>
          handleInputChange(selfKey, credsMeta)
        }
        selectedCredentials={value}
      />
      {errors[selfKey] && (
        <span className="error-message">{errors[selfKey]}</span>
      )}
    </div>
  );
};

const InputRef = (value: any): ((el: HTMLInputElement | null) => void) => {
  return (el) => el && value != null && (el.value = value);
};

const NodeKeyValueInput: FC<{
  nodeId: string;
  selfKey: string;
  schema: BlockIOKVSubSchema;
  entries?: { [key: string]: string } | { [key: string]: number };
  errors: { [key: string]: string | undefined };
  connections: NodeObjectInputTreeProps["connections"];
  handleInputChange: NodeObjectInputTreeProps["handleInputChange"];
  className?: string;
  displayName?: string;
}> = ({
  nodeId,
  selfKey,
  entries,
  schema,
  connections,
  handleInputChange,
  errors,
  className,
  displayName,
}) => {
  const getPairValues = useCallback(() => {
    // Map will preserve the order of entries.
    let inputEntries = entries ?? schema.default;
    if (!inputEntries || typeof inputEntries !== "object") inputEntries = {};

    const defaultEntries = new Map(Object.entries(inputEntries));
    const prefix = `${selfKey}_#_`;
    connections
      .filter((c) => c.targetHandle.startsWith(prefix) && c.target === nodeId)
      .map((c) => c.targetHandle.slice(prefix.length))
      .forEach((k) => !defaultEntries.has(k) && defaultEntries.set(k, ""));

    return Array.from(defaultEntries, ([key, value]) => ({ key, value }));
  }, [entries, schema.default, connections, nodeId, selfKey]);

  const [keyValuePairs, setKeyValuePairs] = useState<
    { key: string; value: string | number | null }[]
  >([]);

  useEffect(
    () => setKeyValuePairs(getPairValues()),
    [connections, entries, schema.default, getPairValues],
  );

  function updateKeyValuePairs(newPairs: typeof keyValuePairs) {
    setKeyValuePairs(newPairs);

    handleInputChange(
      selfKey,
      newPairs.reduce((obj, { key, value }) => ({ ...obj, [key]: value }), {}),
    );
  }

  function convertValueType(value: string): string | number | null {
    if (
      !schema.additionalProperties ||
      schema.additionalProperties.type == "string"
    )
      return value;
    if (!value) return null;
    return Number(value);
  }

  function getEntryKey(key: string): string {
    return `${selfKey}_#_${key}`;
  }
  function isConnected(key: string): boolean {
    return connections.some(
      (c) => c.targetHandle === getEntryKey(key) && c.target === nodeId,
    );
  }

  return (
    <div
      className={cn(className, keyValuePairs.length > 0 ? "flex flex-col" : "")}
    >
      <div>
        {keyValuePairs.map(({ key, value }, index) => (
          // The `index` is used as a DOM key instead of the actual `key`
          // because the `key` can change with each input, causing the input to lose focus.
          <div key={index}>
            <NodeHandle
              keyName={getEntryKey(key)}
              schema={{ type: "string" }}
              isConnected={isConnected(key)}
              isRequired={false}
              side="left"
            />
            {!isConnected(key) && (
              <div className="nodrag mb-2 flex items-center space-x-2">
                <LocalValuedInput
                  type="text"
                  placeholder="Key"
                  value={key ?? ""}
                  onChange={(e) =>
                    updateKeyValuePairs(
                      keyValuePairs.toSpliced(index, 1, {
                        key: e.target.value,
                        value: value,
                      }),
                    )
                  }
                />
                <LocalValuedInput
                  type="text"
                  placeholder="Value"
                  value={value ?? ""}
                  onChange={(e) =>
                    updateKeyValuePairs(
                      keyValuePairs.toSpliced(index, 1, {
                        key: key,
                        value: convertValueType(e.target.value),
                      }),
                    )
                  }
                />
                <Button
                  variant="ghost"
                  className="px-2"
                  onClick={() =>
                    updateKeyValuePairs(keyValuePairs.toSpliced(index, 1))
                  }
                >
                  <Cross2Icon />
                </Button>
              </div>
            )}
            {errors[`${selfKey}.${key}`] && (
              <span className="error-message">
                {errors[`${selfKey}.${key}`]}
              </span>
            )}
          </div>
        ))}
        <Button
          className="bg-gray-200 font-normal text-black hover:text-white dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
          disabled={
            keyValuePairs.length > 0 &&
            !keyValuePairs[keyValuePairs.length - 1].key
          }
          onClick={() =>
            updateKeyValuePairs(keyValuePairs.concat({ key: "", value: "" }))
          }
        >
          <PlusIcon className="mr-2" /> Add Property
        </Button>
      </div>
      {errors[selfKey] && (
        <span className="error-message">{errors[selfKey]}</span>
      )}
    </div>
  );
};

// Checking if schema is type of string
function isStringSubSchema(
  schema: BlockIOSimpleTypeSubSchema,
): schema is BlockIOStringSubSchema {
  return "type" in schema && schema.type === "string";
}

const NodeArrayInput: FC<{
  nodeId: string;
  selfKey: string;
  schema: BlockIOArraySubSchema;
  entries?: string[];
  errors: { [key: string]: string | undefined };
  connections: NodeObjectInputTreeProps["connections"];
  handleInputChange: NodeObjectInputTreeProps["handleInputChange"];
  handleInputClick: NodeObjectInputTreeProps["handleInputClick"];
  className?: string;
  displayName?: string;
}> = ({
  nodeId,
  selfKey,
  schema,
  entries,
  errors,
  connections,
  handleInputChange,
  handleInputClick,
  className,
  displayName,
}) => {
  entries ??= schema.default;
  if (!entries || !Array.isArray(entries)) entries = [];

  const prefix = `${selfKey}_$_`;
  connections
    .filter((c) => c.targetHandle.startsWith(prefix) && c.target === nodeId)
    .map((c) => parseInt(c.targetHandle.slice(prefix.length)))
    .filter((c) => !isNaN(c))
    .forEach(
      (c) =>
        entries.length <= c &&
        entries.push(...Array(c - entries.length + 1).fill("")),
    );

  const isItemObject = "items" in schema && "properties" in schema.items!;
  const error =
    typeof errors[selfKey] === "string" ? errors[selfKey] : undefined;
  return (
    <div className={cn(className, "flex flex-col")}>
      {entries.map((entry: any, index: number) => {
        const entryKey = `${selfKey}_$_${index}`;
        const isConnected =
          connections &&
          connections.some(
            (c) => c.targetHandle === entryKey && c.target === nodeId,
          );
        return (
          <div key={entryKey}>
            <NodeHandle
              keyName={entryKey}
              schema={schema.items!}
              isConnected={isConnected}
              isRequired={false}
              side="left"
            />
            <div className="mb-2 flex space-x-2">
              {!isConnected &&
                (schema.items ? (
                  <NodeGenericInputField
                    className="w-full"
                    nodeId={nodeId}
                    propKey={entryKey}
                    propSchema={schema.items}
                    currentValue={entry}
                    errors={errors}
                    connections={connections}
                    handleInputChange={handleInputChange}
                    handleInputClick={handleInputClick}
                  />
                ) : (
                  <NodeFallbackInput
                    selfKey={entryKey}
                    schema={schema.items}
                    value={entry}
                    error={errors[entryKey]}
                    displayName={displayName || beautifyString(selfKey)}
                    handleInputChange={handleInputChange}
                    handleInputClick={handleInputClick}
                  />
                ))}
              {!isConnected && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() =>
                    handleInputChange(selfKey, entries.toSpliced(index, 1))
                  }
                >
                  <Cross2Icon />
                </Button>
              )}
            </div>
            {errors[entryKey] && typeof errors[entryKey] === "string" && (
              <span className="error-message">{errors[entryKey]}</span>
            )}
          </div>
        );
      })}
      <Button
        className="w-[183p] bg-gray-200 font-normal text-black hover:text-white dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
        onClick={() =>
          handleInputChange(selfKey, [...entries, isItemObject ? {} : ""])
        }
      >
        <PlusIcon className="mr-2" /> Add Item
      </Button>
      {error && <span className="error-message">{error}</span>}
    </div>
  );
};

const NodeMultiSelectInput: FC<{
  selfKey: string;
  schema: BlockIOObjectSubSchema; // TODO: Support BlockIOArraySubSchema
  selection?: string[];
  error?: string;
  className?: string;
  displayName?: string;
  handleInputChange: NodeObjectInputTreeProps["handleInputChange"];
}> = ({
  selfKey,
  schema,
  selection = [],
  error,
  className,
  displayName,
  handleInputChange,
}) => {
  const options = Object.keys(schema.properties);

  return (
    <div className={cn("flex flex-col", className)}>
      <MultiSelector
        className="nodrag"
        values={selection}
        onValuesChange={(v) => handleInputChange(selfKey, v)}
      >
        <MultiSelectorTrigger>
          <MultiSelectorInput
            placeholder={
              schema.placeholder ?? `Select ${displayName || schema.title}...`
            }
          />
        </MultiSelectorTrigger>
        <MultiSelectorContent className="nowheel">
          <MultiSelectorList>
            {options
              .map((key) => ({ ...schema.properties[key], key }))
              .map(({ key, title, description }) => (
                <MultiSelectorItem key={key} value={key} title={description}>
                  {title ?? key}
                </MultiSelectorItem>
              ))}
          </MultiSelectorList>
        </MultiSelectorContent>
      </MultiSelector>
      {error && <span className="error-message">{error}</span>}
    </div>
  );
};

const NodeStringInput: FC<{
  selfKey: string;
  schema: BlockIOStringSubSchema;
  value?: string;
  error?: string;
  handleInputChange: NodeObjectInputTreeProps["handleInputChange"];
  handleInputClick: NodeObjectInputTreeProps["handleInputClick"];
  className?: string;
  displayName: string;
}> = ({
  selfKey,
  schema,
  value = "",
  error,
  handleInputChange,
  handleInputClick,
  className,
  displayName,
}) => {
  value ||= schema.default || "";
  return (
    <div className={className}>
      {schema.enum ? (
        <Select
          defaultValue={value}
          onValueChange={(newValue) => handleInputChange(selfKey, newValue)}
        >
          <SelectTrigger>
            <SelectValue placeholder={schema.placeholder || displayName} />
          </SelectTrigger>
          <SelectContent className="nodrag">
            {schema.enum.map((option, index) => (
              <SelectItem key={index} value={option}>
                {beautifyString(option)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      ) : (
        <div
          className="nodrag relative"
          onClick={schema.secret ? () => handleInputClick(selfKey) : undefined}
        >
          <LocalValuedInput
            type="text"
            id={selfKey}
            value={schema.secret && value ? "*".repeat(value.length) : value}
            onChange={(e) => handleInputChange(selfKey, e.target.value)}
            readOnly={schema.secret}
            placeholder={
              schema?.placeholder || `Enter ${beautifyString(displayName)}`
            }
            className="pr-8 read-only:cursor-pointer read-only:text-gray-500"
          />
          <Button
            variant="ghost"
            size="icon"
            className="absolute inset-1 left-auto h-7 w-7 rounded-[0.25rem]"
            onClick={() => handleInputClick(selfKey)}
            title="Open a larger textbox input"
          >
            <Pencil2Icon className="m-0 p-0" />
          </Button>
        </div>
      )}
      {error && <span className="error-message">{error}</span>}
    </div>
  );
};

export const NodeTextBoxInput: FC<{
  selfKey: string;
  schema: BlockIOStringSubSchema;
  value?: string;
  error?: string;
  handleInputChange: NodeObjectInputTreeProps["handleInputChange"];
  handleInputClick: NodeObjectInputTreeProps["handleInputClick"];
  className?: string;
  displayName: string;
}> = ({
  selfKey,
  schema,
  value = "",
  error,
  handleInputChange,
  handleInputClick,
  className,
  displayName,
}) => {
  value ||= schema.default || "";
  return (
    <div className={className}>
      <div
        className="nodrag relative m-0 h-[200px] w-full bg-yellow-100 p-4 dark:bg-yellow-900"
        onClick={schema.secret ? () => handleInputClick(selfKey) : undefined}
      >
        <textarea
          id={selfKey}
          value={schema.secret && value ? "********" : value}
          readOnly={schema.secret}
          placeholder={
            schema?.placeholder || `Enter ${beautifyString(displayName)}`
          }
          onChange={(e) => handleInputChange(selfKey, e.target.value)}
          className="h-full w-full resize-none overflow-hidden border-none bg-transparent text-lg text-black outline-hidden dark:text-white"
          style={{
            fontSize: "min(1em, 16px)",
            lineHeight: "1.2",
          }}
        />
      </div>
      {error && <span className="error-message">{error}</span>}
    </div>
  );
};

const NodeNumberInput: FC<{
  selfKey: string;
  schema: BlockIONumberSubSchema;
  value?: number;
  error?: string;
  handleInputChange: NodeObjectInputTreeProps["handleInputChange"];
  className?: string;
  displayName?: string;
}> = ({
  selfKey,
  schema,
  value,
  error,
  handleInputChange,
  className,
  displayName,
}) => {
  value ||= schema.default;
  displayName ||= schema.title || beautifyString(selfKey);
  return (
    <div className={className}>
      <div className="nodrag flex items-center justify-between space-x-3">
        <LocalValuedInput
          type="number"
          id={selfKey}
          value={value}
          onChange={(e) =>
            handleInputChange(selfKey, parseFloat(e.target.value))
          }
          placeholder={
            schema.placeholder || `Enter ${beautifyString(displayName)}`
          }
          className="dark:text-white"
        />
      </div>
      {error && <span className="error-message">{error}</span>}
    </div>
  );
};

const NodeBooleanInput: FC<{
  selfKey: string;
  schema: BlockIOBooleanSubSchema;
  value?: boolean;
  error?: string;
  handleInputChange: NodeObjectInputTreeProps["handleInputChange"];
  className?: string;
  displayName: string;
}> = ({
  selfKey,
  schema,
  value,
  error,
  handleInputChange,
  className,
  displayName,
}) => {
  value ||= schema.default ?? false;
  return (
    <div className={className}>
      <div className="nodrag flex items-center">
        <Switch
          defaultChecked={value}
          onCheckedChange={(v) => handleInputChange(selfKey, v)}
        />
        {displayName && (
          <span className="ml-3 dark:text-gray-300">{displayName}</span>
        )}
      </div>
      {error && <span className="error-message">{error}</span>}
    </div>
  );
};

const NodeFallbackInput: FC<{
  selfKey: string;
  schema?: BlockIOSubSchema;
  value: any;
  error?: string;
  handleInputChange: NodeObjectInputTreeProps["handleInputChange"];
  handleInputClick: NodeObjectInputTreeProps["handleInputClick"];
  className?: string;
  displayName: string;
}> = ({
  selfKey,
  schema,
  value,
  error,
  handleInputChange,
  handleInputClick,
  className,
  displayName,
}) => {
  value ||= (schema as BlockIOStringSubSchema)?.default;
  return (
    <NodeStringInput
      selfKey={selfKey}
      schema={{ type: "string", ...schema } as BlockIOStringSubSchema}
      value={value}
      error={error}
      handleInputChange={handleInputChange}
      handleInputClick={handleInputClick}
      className={className}
      displayName={displayName}
    />
  );
};
