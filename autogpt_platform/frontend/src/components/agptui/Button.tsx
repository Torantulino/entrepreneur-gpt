import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center whitespace-nowrap font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-950 disabled:pointer-events-none disabled:opacity-50 dark:focus-visible:ring-neutral-300 font-neue leading-9 tracking-tight",
  {
    variants: {
      variant: {
        destructive:
          "bg-red-600 text-neutral-50 border border-red-500/50 hover:bg-red-500/90 dark:bg-red-700 dark:text-neutral-50 dark:hover:bg-red-600",
        accent: "bg-accent text-accent-foreground hover:bg-violet-500",
        outline:
          "border border-black/50 text-[#272727] hover:bg-neutral-100 dark:bg-neutral-800 dark:text-neutral-100 dark:hover:bg-neutral-700",
        secondary:
          "bg-neutral-100 text-[#272727] border border-neutral-200 hover:bg-neutral-100/80 dark:bg-neutral-700 dark:text-neutral-100 dark:border-neutral-600 dark:hover:bg-neutral-600",
        ghost:
          "hover:bg-neutral-100 text-[#272727] dark:text-neutral-100 dark:hover:bg-neutral-700",
        link: "text-[#272727] underline-offset-4 hover:underline dark:text-neutral-100",
      },
      size: {
        default: "h-10 px-4 py-2 rounded-full text-sm",
        sm: "h-8 px-3 py-1.5 rounded-full text-xs",
        lg: "h-12 px-5 py-2.5 rounded-full text-lg",
        primary:
          "h-10 w-28 rounded-full sm:h-12 sm:w-32 md:h-[4.375rem] md:w-[11rem] lg:h-[3.125rem] lg:w-[7rem]",
        icon: "h-10 w-10",
        card: "h-12 p-5 agpt-rounded-card justify-center text-lg",
      },
    },
    defaultVariants: {
      variant: "outline",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  variant?:
    | "destructive"
    | "accent"
    | "outline"
    | "secondary"
    | "ghost"
    | "link";
  size?: "default" | "sm" | "lg" | "primary" | "icon" | "card";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
