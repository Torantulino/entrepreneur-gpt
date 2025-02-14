import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-[80px] text-xl font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-950 disabled:pointer-events-none disabled:opacity-50 dark:focus-visible:ring-neutral-300 font-neue leading-9 tracking-tight",
  {
    variants: {
      variant: {
        default:
          "bg-white border border-black/50 text-[#272727] hover:bg-neutral-100 dark:bg-neutral-800 dark:text-neutral-100 dark:hover:bg-neutral-700",
        destructive:
          "bg-red-600 text-neutral-50 border border-red-500/50 hover:bg-red-500/90 dark:bg-red-700 dark:text-neutral-50 dark:hover:bg-red-600",
        outline:
          "bg-white border border-black/50 text-[#272727] hover:bg-neutral-100 dark:bg-neutral-800 dark:text-neutral-100 dark:hover:bg-neutral-700",
        secondary:
          "bg-neutral-100 text-[#272727] border border-neutral-200 hover:bg-neutral-100/80 dark:bg-neutral-700 dark:text-neutral-100 dark:border-neutral-600 dark:hover:bg-neutral-600",
        ghost:
          "hover:bg-neutral-100 text-[#272727] dark:text-neutral-100 dark:hover:bg-neutral-700",
        link: "text-[#272727] underline-offset-4 hover:underline dark:text-neutral-100",
        library_outline:
          "rounded-[52px] hover:bg-[#262626] border border-zinc-700 hover:text-white font-sans",
        library_primary: "rounded-[52px] bg-[#262626] text-white font-sans",
      },
      size: {
        default:
          "h-10 px-4 py-2 text-sm sm:h-12 sm:px-5 sm:py-2.5 sm:text-base md:h-14 md:px-6 md:py-3 md:text-lg lg:h-[4.375rem] lg:px-[1.625rem] lg:py-[0.4375rem] lg:text-xl",
        sm: "h-8 px-3 py-1.5 text-xs sm:h-9 sm:px-3.5 sm:py-2 sm:text-sm md:h-10 md:px-4 md:py-2 md:text-base lg:h-[3.125rem] lg:px-[1.25rem] lg:py-[0.3125rem] lg:text-sm",
        lg: "h-12 px-5 py-2.5 text-lg sm:h-14 sm:px-6 sm:py-3 sm:text-xl md:h-16 md:px-7 md:py-3.5 md:text-2xl lg:h-[5.625rem] lg:px-[2rem] lg:py-[0.5625rem] lg:text-2xl",
        primary:
          "h-10 w-28 sm:h-12 sm:w-32 md:h-[4.375rem] md:w-[11rem] lg:h-[3.125rem] lg:w-[7rem]",
        icon: "h-10 w-10 sm:h-12 sm:w-12 md:h-14 md:w-14 lg:h-[4.375rem] lg:w-[4.375rem]",
        library: "py-2 px-[14px] h-10 text-[14px] font-medium leading-6 ",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  variant?:
    | "default"
    | "destructive"
    | "outline"
    | "secondary"
    | "ghost"
    | "link"
    | "library_outline"
    | "library_primary";

  size?: "default" | "sm" | "lg" | "primary" | "icon" | "library";
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
