import Avatar from "boring-avatars";

import React from "react";

interface BoringAvatarWrapperProps {
  size?: number;
  name: string;
  variant?: "marble" | "beam" | "pixel" | "sunset" | "ring-3" | "bauhaus";
  colors?: string[];
  square?: boolean;
}

export const BoringAvatarWrapper: React.FC<BoringAvatarWrapperProps> = ({
  size = 40,
  name,
  variant = "beam",
  colors = ["#92A1C6", "#146A7C", "#F0AB3D", "#C271B4", "#C20D90"],
  square = false,
}) => {
  return (
    <Avatar
      size={size}
      name={name}
      variant={variant}
      colors={colors}
      square={square}
    />
  );
};

export default BoringAvatarWrapper;
