import AutoGPTServerAPI from "@/lib/autogpt-server-api";
import {
  RefundRequest,
  TransactionHistory,
} from "@/lib/autogpt-server-api/types";
import { useCallback, useEffect, useMemo, useState } from "react";
import { loadStripe, Stripe } from "@stripe/stripe-js";
import { useRouter } from "next/navigation";

export default function useCredits({
  fetchInitialCredits = false,
  fetchInitialAutoTopUpConfig = false,
  fetchInitialTransactionHistory = false,
  fetchInitialRefundRequests = false,
  fetchTopUpLibrary = false,
}: {
  fetchInitialCredits?: boolean;
  fetchInitialAutoTopUpConfig?: boolean;
  fetchInitialTransactionHistory?: boolean;
  fetchInitialRefundRequests?: boolean;
  fetchTopUpLibrary?: boolean;
} = {}): {
  credits: number | null;
  fetchCredits: () => void;
  requestTopUp: (credit_amount: number) => Promise<void>;
  refundTopUp: (transaction_key: string, reason: string) => Promise<number>;
  autoTopUpConfig: { amount: number; threshold: number } | null;
  fetchAutoTopUpConfig: () => void;
  updateAutoTopUpConfig: (amount: number, threshold: number) => Promise<void>;
  transactionHistory: TransactionHistory;
  fetchTransactionHistory: () => void;
  refundRequests: RefundRequest[];
  fetchRefundRequests: () => void;
  formatCredits: (credit: number | null) => string;
} {
  const [credits, setCredits] = useState<number | null>(null);
  const [autoTopUpConfig, setAutoTopUpConfig] = useState<{
    amount: number;
    threshold: number;
  } | null>(null);
  const [stripe, setStripe] = useState<Stripe | null>(null);

  const api = useMemo(() => new AutoGPTServerAPI(), []);
  const router = useRouter();

  const fetchCredits = useCallback(async () => {
    const response = await api.getUserCredit();
    setCredits(response.credits);
  }, [api]);

  useEffect(() => {
    if (!fetchInitialCredits) return;
    fetchCredits();
  }, [fetchCredits, fetchInitialCredits]);

  useEffect(() => {
    if (!fetchTopUpLibrary) return;
    const fetchStripe = async () => {
      if (!process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY?.trim()) {
        console.debug("Stripe publishable key is not set.");
        return;
      }
      const stripe = await loadStripe(
        process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY,
      );
      setStripe(stripe);
    };
    fetchStripe();
  }, [fetchTopUpLibrary]);

  const fetchAutoTopUpConfig = useCallback(async () => {
    const response = await api.getAutoTopUpConfig();
    setAutoTopUpConfig(response);
  }, [api]);

  useEffect(() => {
    if (!fetchInitialAutoTopUpConfig) return;
    fetchAutoTopUpConfig();
  }, [fetchAutoTopUpConfig, fetchInitialAutoTopUpConfig]);

  const updateAutoTopUpConfig = useCallback(
    async (amount: number, threshold: number) => {
      await api.setAutoTopUpConfig({ amount, threshold });
      fetchAutoTopUpConfig();
    },
    [api, fetchAutoTopUpConfig],
  );

  const requestTopUp = useCallback(
    async (credit_amount: number) => {
      if (!stripe) {
        console.error(
          "Trying to top-up failed because Stripe is not loaded." +
            "Did you set NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY?",
        );
        return;
      }

      const response = await api.requestTopUp(credit_amount);
      router.push(response.checkout_url);
    },
    [api, router, stripe],
  );

  const refundTopUp = useCallback(
    async (transaction_key: string, reason: string) => {
      const refunded_amount = await api.refundTopUp(transaction_key, reason);
      await fetchCredits();
      setTransactionHistory(await api.getTransactionHistory());
      return refunded_amount;
    },
    [api, fetchCredits],
  );

  const [transactionHistory, setTransactionHistory] =
    useState<TransactionHistory>({
      transactions: [],
      next_transaction_time: null,
    });

  const fetchTransactionHistory = useCallback(async () => {
    const response = await api.getTransactionHistory(
      transactionHistory.next_transaction_time,
      20,
    );
    setTransactionHistory({
      transactions: [
        ...transactionHistory.transactions,
        ...response.transactions,
      ],
      next_transaction_time: response.next_transaction_time,
    });
  }, [api, transactionHistory]);

  useEffect(() => {
    if (!fetchInitialTransactionHistory) return;
    fetchTransactionHistory();
    // Note: We only need to fetch transaction history once.
    // Hence, we should avoid `fetchTransactionHistory` to the dependency array.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetchInitialTransactionHistory]);

  const [refundRequests, setRefundRequests] = useState<RefundRequest[]>([]);

  const fetchRefundRequests = useCallback(async () => {
    const response = await api.getRefundRequests();
    setRefundRequests(response);
  }, [api]);

  useEffect(() => {
    if (!fetchInitialRefundRequests) return;
    fetchRefundRequests();
  }, [fetchRefundRequests, fetchInitialRefundRequests]);

  const formatCredits = useCallback((credit: number | null) => {
    if (credit === null) {
      return "-";
    }
    const value = Math.abs(credit);
    const sign = credit < 0 ? "-" : "";
    const precision =
      2 - (value % 100 === 0 ? 1 : 0) - (value % 10 === 0 ? 1 : 0);
    return `${sign}$${(value / 100).toFixed(precision)}`;
  }, []);

  return {
    credits,
    fetchCredits,
    requestTopUp,
    refundTopUp,
    autoTopUpConfig,
    fetchAutoTopUpConfig,
    updateAutoTopUpConfig,
    transactionHistory,
    fetchTransactionHistory,
    refundRequests,
    fetchRefundRequests,
    formatCredits,
  };
}
