import React, { useState } from "react";
import { X, ArrowUpRight, ArrowDownLeft } from "lucide-react";

export default function TransactionModal({
  isOpen,
  onClose,
  onSave,
  customerId,
  customerName = "Customer",
  defaultType = "gave_credit",
}) {
  const [amount, setAmount] = useState("");
  const [transactionType, setTransactionType] = useState(defaultType);
  const [dueDate, setDueDate] = useState("");
  const [status, setStatus] = useState("pending");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      setError("Please enter a valid amount greater than 0.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const payload = {
        customer_id: customerId,
        amount: parsedAmount.toFixed(2),
        transaction_type: transactionType,
        status: transactionType === "received_payment" ? "paid" : status,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
      };

      await onSave(payload);
      onClose();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to record transaction.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <div className="modal-header">
          <div className="modal-title-wrap">
            <h3>Record Entry for {customerName}</h3>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          {error && <div className="alert-error">{error}</div>}

          {/* Toggle Type */}
          <div className="type-toggle-group">
            <button
              type="button"
              className={`toggle-option credit ${transactionType === "gave_credit" ? "selected" : ""}`}
              onClick={() => {
                setTransactionType("gave_credit");
                setStatus("pending");
              }}
            >
              <ArrowUpRight size={18} />
              <span>Gave Credit (उधार दिया)</span>
            </button>
            <button
              type="button"
              className={`toggle-option payment ${transactionType === "received_payment" ? "selected" : ""}`}
              onClick={() => {
                setTransactionType("received_payment");
                setStatus("paid");
              }}
            >
              <ArrowDownLeft size={18} />
              <span>Received Payment (जमा मिला)</span>
            </button>
          </div>

          <div className="form-group">
            <label>Amount (₹)</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              placeholder="0.00"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
              autoFocus
            />
          </div>

          {transactionType === "gave_credit" && (
            <>
              <div className="form-group">
                <label>Expected Due Date (Optional)</label>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Status</label>
                <select value={status} onChange={(e) => setStatus(e.target.value)}>
                  <option value="pending">Pending</option>
                  <option value="overdue">Overdue</option>
                  <option value="paid">Paid</option>
                </select>
              </div>
            </>
          )}

          <div className="modal-actions">
            <button type="button" className="secondary-btn" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button
              type="submit"
              className={`primary-btn ${transactionType === "gave_credit" ? "btn-danger" : "btn-success"}`}
              disabled={loading}
            >
              {loading ? "Recording..." : "Save Entry"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
