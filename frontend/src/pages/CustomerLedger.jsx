import React, { useState, useEffect } from "react";
import {
  ArrowLeft,
  ArrowUpRight,
  ArrowDownLeft,
  Calendar,
  Clock,
  Trash2,
  Edit2,
  Phone,
  User,
  Plus,
  AlertCircle,
} from "lucide-react";
import { formatCurrency, formatDate, formatDateTime } from "../utils/formatters";
import {
  getCustomer,
  createTransaction,
  deleteTransaction,
  deleteCustomer,
  updateCustomer,
} from "../services/api";
import TransactionModal from "../components/TransactionModal";
import CustomerModal from "../components/CustomerModal";

export default function CustomerLedger({ customerId, onBack }) {
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isTxModalOpen, setIsTxModalOpen] = useState(false);
  const [txModalType, setTxModalType] = useState("gave_credit");
  const [isEditCustomerOpen, setIsEditCustomerOpen] = useState(false);

  const loadCustomer = async () => {
    try {
      setLoading(true);
      const data = await getCustomer(customerId);
      setCustomer(data);
    } catch (err) {
      console.error("Failed to load customer:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (customerId) {
      loadCustomer();
    }
  }, [customerId]);

  const handleOpenTransaction = (type) => {
    setTxModalType(type);
    setIsTxModalOpen(true);
  };

  const handleSaveTransaction = async (txData) => {
    await createTransaction(txData);
    await loadCustomer();
  };

  const handleDeleteTransaction = async (txId) => {
    if (window.confirm("Are you sure you want to delete this transaction entry?")) {
      await deleteTransaction(txId);
      await loadCustomer();
    }
  };

  const handleDeleteCustomer = async () => {
    if (
      window.confirm(
        `Are you sure you want to delete ${customer.name}? All ledger records will be permanently removed.`
      )
    ) {
      await deleteCustomer(customer.id);
      onBack();
    }
  };

  const handleUpdateCustomer = async (data) => {
    await updateCustomer(customer.id, data);
    await loadCustomer();
  };

  if (loading) {
    return <div className="loading-state">Loading ledger...</div>;
  }

  if (!customer) {
    return (
      <div className="empty-state">
        <p>Customer not found.</p>
        <button className="secondary-btn" onClick={onBack}>
          Back to Dashboard
        </button>
      </div>
    );
  }

  const outstanding = parseFloat(customer.total_outstanding || 0);

  return (
    <div className="ledger-container">
      {/* Header bar */}
      <div className="ledger-header">
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={18} />
          <span>Back to Dashboard</span>
        </button>

        <div className="ledger-actions-header">
          <button
            className="secondary-btn"
            onClick={() => setIsEditCustomerOpen(true)}
          >
            <Edit2 size={16} />
            <span>Edit Profile</span>
          </button>
          <button className="delete-btn" onClick={handleDeleteCustomer}>
            <Trash2 size={16} />
            <span>Delete Customer</span>
          </button>
        </div>
      </div>

      {/* Customer Summary Card */}
      <div className="customer-summary-card">
        <div className="summary-left">
          <div className="avatar-large">
            {customer.name.charAt(0).toUpperCase()}
          </div>
          <div className="customer-meta">
            <h2>{customer.name}</h2>
            <p className="phone-line">
              <Phone size={16} />
              <span>{customer.phone}</span>
            </p>
          </div>
        </div>

        <div className="summary-right">
          <div className="balance-box">
            <span className="balance-label">Net Balance (बाकी राशि)</span>
            <h1
              className={`balance-number ${
                outstanding > 0 ? "text-danger" : "text-success"
              }`}
            >
              {formatCurrency(outstanding)}
            </h1>
            <span className="balance-sublabel">
              {outstanding > 0
                ? "You will receive from customer"
                : outstanding < 0
                ? "You owe the customer"
                : "No pending balance"}
            </span>
          </div>

          <div className="ledger-quick-buttons">
            <button
              className="credit-btn"
              onClick={() => handleOpenTransaction("gave_credit")}
            >
              <ArrowUpRight size={18} />
              <span>Gave Credit (उधार दिया)</span>
            </button>
            <button
              className="payment-btn"
              onClick={() => handleOpenTransaction("received_payment")}
            >
              <ArrowDownLeft size={18} />
              <span>Received (जमा मिला)</span>
            </button>
          </div>
        </div>
      </div>

      {/* Transactions List */}
      <div className="transactions-section">
        <div className="tx-section-header">
          <h3>Transaction History ({customer.transactions?.length || 0})</h3>
        </div>

        {customer.transactions?.length === 0 ? (
          <div className="empty-tx-state">
            <p>No transactions yet for this customer.</p>
            <button
              className="primary-btn"
              onClick={() => handleOpenTransaction("gave_credit")}
            >
              Add First Entry
            </button>
          </div>
        ) : (
          <div className="tx-table-wrap">
            <table className="tx-table">
              <thead>
                <tr>
                  <th>Date & Time</th>
                  <th>Type</th>
                  <th>Due Date</th>
                  <th>Status</th>
                  <th>Amount</th>
                  <th style={{ textAlign: "right" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {customer.transactions.map((tx) => {
                  const isCredit = tx.transaction_type === "gave_credit";
                  return (
                    <tr key={tx.id}>
                      <td>{formatDateTime(tx.created_at)}</td>
                      <td>
                        <span
                          className={`tx-type-tag ${
                            isCredit ? "tag-credit" : "tag-payment"
                          }`}
                        >
                          {isCredit ? "Gave Credit" : "Payment Received"}
                        </span>
                      </td>
                      <td>
                        {tx.due_date ? (
                          <span className="due-date-text">
                            <Calendar size={14} />
                            {formatDate(tx.due_date)}
                          </span>
                        ) : (
                          <span className="text-muted">—</span>
                        )}
                      </td>
                      <td>
                        <span className={`status-pill status-${tx.status}`}>
                          {tx.status}
                        </span>
                      </td>
                      <td>
                        <strong
                          className={isCredit ? "text-danger" : "text-success"}
                        >
                          {isCredit ? "-" : "+"}{formatCurrency(tx.amount)}
                        </strong>
                      </td>
                      <td style={{ textAlign: "right" }}>
                        <button
                          className="icon-action-btn delete"
                          onClick={() => handleDeleteTransaction(tx.id)}
                          title="Delete entry"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Transaction Modal */}
      <TransactionModal
        isOpen={isTxModalOpen}
        onClose={() => setIsTxModalOpen(false)}
        onSave={handleSaveTransaction}
        customerId={customer.id}
        customerName={customer.name}
        defaultType={txModalType}
      />

      {/* Edit Customer Modal */}
      <CustomerModal
        isOpen={isEditCustomerOpen}
        onClose={() => setIsEditCustomerOpen(false)}
        onSave={handleUpdateCustomer}
        customer={customer}
      />
    </div>
  );
}
