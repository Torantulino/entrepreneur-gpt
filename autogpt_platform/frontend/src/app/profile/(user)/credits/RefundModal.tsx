import { useState } from "react";
import { AlertCircle } from "lucide-react";

import { CreditTransaction } from "@/lib/autogpt-server-api";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

interface RefundModalProps {
  isOpen: boolean;
  onClose: () => void;
  transactions: CreditTransaction[];
  formatCredits: (credit: number) => string;
  refundCredits: (transaction_key: string, reason: string) => Promise<void>;
}

export const RefundModal = ({
  isOpen,
  onClose,
  transactions,
  formatCredits,
  refundCredits,
}: RefundModalProps) => {
  const [selectedTransactionId, setSelectedTransactionId] =
    useState<string>("");
  const [refundReason, setRefundReason] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleClose = () => {
    setSelectedTransactionId("");
    setRefundReason("");
    setError(null);
    onClose();
  };

  const handleRefundRequest = () => {
    setError(null);

    const selectedTransaction = transactions.find(
      (t) => t.transaction_key === selectedTransactionId,
    );

    if (!selectedTransaction) {
      setError("Please select a transaction to refund");
      return;
    }

    if (refundReason.trim().length < 20) {
      setError("Please provide a clear reason for the refund");
      return;
    }

    refundCredits(selectedTransactionId, refundReason).finally(() =>
      handleClose(),
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Request Refund</DialogTitle>
        </DialogHeader>
        <div className="py-4">
          <div className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 rounded-md border border-destructive bg-destructive/10 p-3 text-sm text-destructive">
                <AlertCircle className="h-4 w-4" />
                <p>{error}</p>
              </div>
            )}

            {transactions.length === 0 ? (
              <p className="text-sm text-gray-500">
                No eligible transactions found for refund.
              </p>
            ) : (
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Select Transaction
                </label>
                <Select
                  value={selectedTransactionId}
                  onValueChange={setSelectedTransactionId}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a transaction" />
                  </SelectTrigger>
                  <SelectContent>
                    {transactions.map((transaction) => (
                      <SelectItem
                        key={transaction.transaction_key}
                        value={transaction.transaction_key}
                      >
                        {new Date(transaction.transaction_time).toLocaleString(
                          undefined,
                          {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                            hour: "numeric",
                            minute: "numeric",
                          },
                        )}{" "}
                        - {formatCredits(transaction.amount)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div className="space-y-2">
              <label htmlFor="refundReason" className="text-sm font-medium">
                Reason for Refund
              </label>
              <Textarea
                id="refundReason"
                placeholder="Please explain why you're requesting a refund..."
                value={refundReason}
                onChange={(e) => setRefundReason(e.target.value)}
                className="min-h-[100px]"
              />
            </div>
          </div>
        </div>
        <div className="flex justify-end space-x-4">
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button onClick={handleRefundRequest}>Request Refund</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
