import { useEffect, useState } from "react";

interface ThresholdCallback<T> {
  (value: T): void;
}

export const useThreshold = <T>(
  callback: ThresholdCallback<T>,
  threshold: number,
): boolean => {
  const [prevValue, setPrevValue] = useState<T | null>(null);
  const [isThresholdMet, setIsThresholdMet] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const { scrollY } = window;

      if (scrollY >= threshold) {
        setIsThresholdMet(true);
      } else {
        setIsThresholdMet(false);
      }

      if (scrollY >= threshold && (!prevValue || prevValue !== scrollY)) {
        callback(scrollY as T);
        setPrevValue(scrollY as T);
      }
    };

    window.addEventListener("scroll", handleScroll);
    handleScroll();

    return () => window.removeEventListener("scroll", handleScroll);
  }, [callback, threshold, prevValue]);

  return isThresholdMet;
};
