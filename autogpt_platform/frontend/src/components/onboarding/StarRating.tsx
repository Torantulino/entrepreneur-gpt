import { cn } from "@/lib/utils";
import { FaRegStar, FaStar, FaStarHalfAlt } from "react-icons/fa";

export default function StarRating({
  className,
  starSize,
  rating,
}: {
  className?: string;
  starSize?: number;
  rating: number;
}) {
  // Round to 1 decimal place
  const roundedRating = Math.round(rating * 10) / 10;
  starSize ??= 15;

  // Generate array of 5 star values
  const stars = Array(5)
    .fill(0)
    .map((_, index) => {
      const difference = roundedRating - index;

      if (difference >= 1) {
        return "full";
      } else if (difference > 0) {
        // Half star for values between 0.2 and 0.8
        return difference >= 0.8
          ? "full"
          : difference >= 0.2
            ? "half"
            : "empty";
      }
      return "empty";
    });

  return (
    <div
      className={cn(
        "font-geist flex items-center gap-0.5 text-sm font-medium text-zinc-800",
        className,
      )}
    >
      {/* Display numerical rating */}
      <span className="mr-1 mt-1">{roundedRating}</span>

      {/* Display stars */}
      {stars.map((starType, index) => {
        if (starType === "full") {
          return <FaStar size={starSize} key={index} />;
        } else if (starType === "half") {
          return <FaStarHalfAlt size={starSize} key={index} />;
        } else {
          return <FaRegStar size={starSize} key={index} />;
        }
      })}
    </div>
  );
}
