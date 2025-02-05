import React, { FC, useEffect, useState } from "react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Maximize2, Minimize2, Clipboard } from "lucide-react";
import { createPortal } from "react-dom";
import { toast } from "./ui/use-toast";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (value: string) => void;
  title?: string;
  defaultValue: string;
}

const InputModalComponent: FC<ModalProps> = ({
  isOpen,
  onClose,
  onSave,
  title,
  defaultValue,
}) => {
  const [tempValue, setTempValue] = useState(defaultValue);
  const [isMaximized, setIsMaximized] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setTempValue(defaultValue);
      setIsMaximized(false);
    }
  }, [isOpen, defaultValue]);

  const handleSave = () => {
    onSave(tempValue);
    onClose();
  };

  const toggleSize = () => {
    setIsMaximized(!isMaximized);
  };

  const copyValue = () => {
    navigator.clipboard.writeText(tempValue).then(() => {
      toast({
        title: "Input value copied to clipboard!",
        duration: 2000,
      });
    });
  };

  if (!isOpen) {
    return null;
  }

  const modalContent = (
    <div
      id="modal-content"
      className={`fixed rounded-lg border-[1.5px] bg-white p-5 ${
        isMaximized ? "inset-[128px] flex flex-col" : `w-[90%] max-w-[800px]`
      }`}
    >
      <h2 className="mb-4 text-center text-lg font-semibold">
        {title || "Enter input text"}
      </h2>
      <div className="nowheel relative grow">
        <Textarea
          className="h-full min-h-[200px] w-full resize-none"
          value={tempValue}
          onChange={(e) => setTempValue(e.target.value)}
        />
        <div className="absolute bottom-2 right-2 flex space-x-2">
          <Button onClick={copyValue} size="icon" variant="outline">
            <Clipboard size={18} />
          </Button>
          <Button onClick={toggleSize} size="icon" variant="outline">
            {isMaximized ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </Button>
        </div>
      </div>
      <div className="mt-4 flex justify-end space-x-2">
        <Button onClick={onClose} variant="outline">
          Cancel
        </Button>
        <Button onClick={handleSave}>Save</Button>
      </div>
    </div>
  );

  return (
    <>
      {isMaximized ? (
        createPortal(
          <div className="fixed inset-0 flex items-center justify-center bg-white bg-opacity-60">
            {modalContent}
          </div>,
          document.body,
        )
      ) : (
        <div className="nodrag fixed inset-0 flex items-center justify-center bg-white bg-opacity-60">
          {modalContent}
        </div>
      )}
    </>
  );
};

export default InputModalComponent;
