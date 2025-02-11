import { ChevronLeft } from "lucide-react";
import Link from "next/link";

interface OnboardingBackButtonProps {
  href: string;
}

export default function OnboardingBackButton({ href }: OnboardingBackButtonProps) {
  return (
    <Link
      className="
          font-geist text-base font-medium
          flex items-center gap-2 
          text-zinc-700 hover:text-zinc-800 
          transition-colors duration-200
        "
      href={href}
    >
      <ChevronLeft size={24} className="-mr-1"/>
      <span>Back</span>
    </Link>
  );
};
