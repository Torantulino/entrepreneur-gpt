import { ChevronLeft } from "lucide-react";
import Link from "next/link";

interface OnboardingBackButtonProps {
  href: string;
}

export default function OnboardingBackButton({
  href,
}: OnboardingBackButtonProps) {
  return (
    <Link
      className="flex items-center gap-2 font-sans text-base font-medium text-zinc-700 transition-colors duration-200 hover:text-zinc-800"
      href={href}
    >
      <ChevronLeft size={24} className="-mr-1" />
      <span>Back</span>
    </Link>
  );
}
