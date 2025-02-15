import { cn } from "@/lib/utils";
import Link from "next/link";

const variants = {
  default: "bg-zinc-700 hover:bg-zinc-800",
  violet: "bg-violet-600 hover:bg-violet-700",
};

type OnboardingButtonProps = {
  className?: string;
  variant?: keyof typeof variants;
  children?: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
  href?: string;
};

export default function OnboardingButton({
  className,
  variant = "default",
  children,
  disabled,
  onClick,
  href,
}: OnboardingButtonProps) {
  const buttonClasses = cn(
    "font-sans text-white text-sm font-medium",
    "inline-flex justify-center items-center",
    "h-12 min-w-[100px] rounded-full py-3 px-5 gap-2.5",
    "transition-colors duration-200",
    className,
    disabled ? "bg-zinc-300 cursor-not-allowed" : variants[variant],
  );

  if (href && !disabled) {
    return (
      <Link href={href} className={buttonClasses}>
        {children}
      </Link>
    );
  }

  return (
    <button onClick={onClick} disabled={disabled} className={buttonClasses}>
      {children}
    </button>
  );
}
