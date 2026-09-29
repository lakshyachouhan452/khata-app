import React, { useState, useEffect } from "react";
import {
  TrendingUp,
  Calendar,
  AlertOctagon,
  MessageCircle,
  RefreshCw,
  Search,
  Phone,
  User,
  ArrowUpRight,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import {
  getCustomers,
  getExpectedNextWeek,
  getOverdueCustomers,
  generateWhatsAppReminderLink,
} from "../services/api";

export default function Dashboard() {
  const [totalOutstanding, setTotalOutstanding] = useState(0);
  const [expectedNextWeek, setExpectedNextWeek] = useState({
    amount: 0,
    count: 0,
  });
  const [overdueAccounts, setOverdueAccounts] = useState([]);
  const [filteredOverdue, setFilteredOverdue] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // Currency Formatter
  const formatCurrency = (val) => {
    const num = parseFloat(val) || 0;
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2,
    }).format(num);
  };

  const fetchDashboardData = async () => {
    try {
      setError(null);
      const [customersData, expectedData, overdueData] = await Promise.all([
        getCustomers(),
        getExpectedNextWeek(),
        getOverdueCustomers(),
      ]);

      // Calculate Total Outstanding across all customers
      const total = customersData.reduce(
        (sum, cust) => sum + parseFloat(cust.total_outstanding || 0),
        0
      );
      setTotalOutstanding(total);

      // Expected Next Week
      setExpectedNextWeek({
        amount: parseFloat(expectedData.total_expected_amount || 0),
        count: expectedData.transaction_count || 0,
      });

      // Overdue Customers list
      const overdueList = Array.isArray(overdueData) ? overdueData : [];
      setOverdueAccounts(overdueList);
      setFilteredOverdue(overdueList);
    } catch (err) {
      console.error("Dashboard data fetch error:", err);
      setError("Unable to connect to the backend server. Please verify FastAPI is running at http://localhost:8000.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Filter overdue accounts by search query
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredOverdue(overdueAccounts);
    } else {
      const q = searchQuery.toLowerCase();
      setFilteredOverdue(
        overdueAccounts.filter(
          (item) =>
            item.customer.name.toLowerCase().includes(q) ||
            item.customer.phone.toLowerCase().includes(q)
        )
      );
    }
  }, [searchQuery, overdueAccounts]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  // WhatsApp Reminder Action
  const handleSendReminder = (customer, overdueAmount) => {
    const formattedAmount = formatCurrency(overdueAmount);
    const link = generateWhatsAppReminderLink(
      customer.phone,
      customer.name,
      formattedAmount
    );
    window.open(link, "_blank", "noopener,noreferrer");
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
              <span>📒</span>
              <span>Shopkeeper's Khata Notebook</span>
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Real-time ledger overview, 7-day expected receivables, and overdue collections
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing || loading}
            className="inline-flex items-center justify-center gap-2 self-start sm:self-auto px-4 py-2.5 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 hover:text-slate-900 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <RefreshCw
              size={16}
              className={`${refreshing ? "animate-spin text-blue-600" : ""}`}
            />
            <span>{refreshing ? "Refreshing..." : "Refresh Data"}</span>
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3 text-red-800">
            <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div className="text-sm">
              <span className="font-semibold">Backend Connection Warning:</span> {error}
            </div>
          </div>
        )}

        {/* 3 Main Summary Cards */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-5">
          
          {/* Card 1: Total Outstanding */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-rose-500" />
            <div className="flex items-center justify-between text-slate-500 mb-3">
              <span className="text-sm font-semibold uppercase tracking-wider text-slate-500">
                Total Outstanding
              </span>
              <div className="w-10 h-10 rounded-xl bg-rose-50 flex items-center justify-center text-rose-600">
                <TrendingUp size={20} />
              </div>
            </div>
            <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
              {loading ? (
                <div className="h-9 w-36 bg-slate-200 animate-pulse rounded" />
              ) : (
                <span className="text-rose-600">{formatCurrency(totalOutstanding)}</span>
              )}
            </div>
            <p className="mt-2 text-xs text-slate-500">
              Total credit currently given to customers across all accounts
            </p>
          </div>

          {/* Card 2: Expected Next Week */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-amber-500" />
            <div className="flex items-center justify-between text-slate-500 mb-3">
              <span className="text-sm font-semibold uppercase tracking-wider text-slate-500">
                Expected Next Week
              </span>
              <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600">
                <Calendar size={20} />
              </div>
            </div>
            <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
              {loading ? (
                <div className="h-9 w-36 bg-slate-200 animate-pulse rounded" />
              ) : (
                <span className="text-amber-600">{formatCurrency(expectedNextWeek.amount)}</span>
              )}
            </div>
            <p className="mt-2 text-xs text-slate-500">
              {expectedNextWeek.count} credit invoice{expectedNextWeek.count === 1 ? "" : "s"} scheduled for recovery in next 7 days
            </p>
          </div>

          {/* Card 3: Overdue Accounts */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-red-600" />
            <div className="flex items-center justify-between text-slate-500 mb-3">
              <span className="text-sm font-semibold uppercase tracking-wider text-slate-500">
                Overdue Accounts
              </span>
              <div className="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center text-red-600">
                <AlertOctagon size={20} />
              </div>
            </div>
            <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
              {loading ? (
                <div className="h-9 w-24 bg-slate-200 animate-pulse rounded" />
              ) : (
                <span className="text-red-600">{overdueAccounts.length}</span>
              )}
            </div>
            <p className="mt-2 text-xs text-slate-500">
              Customers requiring immediate reminders due to lapsed payment dates
            </p>
          </div>

        </section>

        {/* Overdue Customers Section */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          
          {/* Table Header & Search */}
          <div className="p-5 sm:p-6 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="flex h-3 w-3 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                </span>
                <h2 className="text-lg font-bold text-slate-900">Overdue Customers List</h2>
              </div>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Showing customers with unpaid bills that have crossed their due date
              </p>
            </div>

            {/* Search Input */}
            <div className="relative w-full sm:w-72">
              <Search
                size={16}
                className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
              />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search overdue customer..."
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
              />
            </div>
          </div>

          {/* Table Container */}
          {loading ? (
            <div className="p-12 text-center text-slate-400">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-slate-200 border-t-blue-600 mb-3" />
              <p className="text-sm">Loading overdue customer records...</p>
            </div>
          ) : filteredOverdue.length === 0 ? (
            <div className="p-12 text-center">
              <div className="w-14 h-14 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-3">
                <CheckCircle2 size={32} />
              </div>
              <h3 className="text-base font-semibold text-slate-800">
                {searchQuery ? "No matching overdue customers" : "All Clear! No Overdue Accounts"}
              </h3>
              <p className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">
                {searchQuery
                  ? `No overdue accounts found matching "${searchQuery}".`
                  : "All customer payments are on track or settled. Good job!"}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50/75 border-b border-slate-200 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    <th className="py-3.5 px-6">Customer Name</th>
                    <th className="py-3.5 px-6">Phone Number</th>
                    <th className="py-3.5 px-6">Overdue Amount</th>
                    <th className="py-3.5 px-6 text-center">Overdue Invoices</th>
                    <th className="py-3.5 px-6 text-right">Reminder Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 text-sm">
                  {filteredOverdue.map((item) => {
                    const cust = item.customer;
                    const amount = item.overdue_amount;
                    const invoiceCount = item.overdue_transactions?.length || 1;

                    return (
                      <tr
                        key={cust.id}
                        className="hover:bg-slate-50/80 transition-colors"
                      >
                        {/* Customer */}
                        <td className="py-4 px-6">
                          <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center flex-shrink-0 text-sm shadow-sm">
                              {cust.name.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <div className="font-semibold text-slate-900">
                                {cust.name}
                              </div>
                              <div className="text-xs text-slate-400">
                                ID: #{cust.id}
                              </div>
                            </div>
                          </div>
                        </td>

                        {/* Phone */}
                        <td className="py-4 px-6 text-slate-600">
                          <div className="flex items-center gap-2">
                            <Phone size={14} className="text-slate-400" />
                            <span>{cust.phone}</span>
                          </div>
                        </td>

                        {/* Overdue Amount */}
                        <td className="py-4 px-6">
                          <span className="inline-flex items-center px-2.5 py-1 rounded-md text-sm font-bold bg-red-50 text-red-700 border border-red-200">
                            {formatCurrency(amount)}
                          </span>
                        </td>

                        {/* Overdue Invoices Count */}
                        <td className="py-4 px-6 text-center">
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
                            {invoiceCount} bill{invoiceCount === 1 ? "" : "s"}
                          </span>
                        </td>

                        {/* Action: Send Reminder */}
                        <td className="py-4 px-6 text-right">
                          <button
                            onClick={() => handleSendReminder(cust, amount)}
                            className="inline-flex items-center gap-2 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white rounded-lg text-xs sm:text-sm font-semibold shadow-sm hover:shadow transition-all focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-1"
                            title={`Send WhatsApp reminder to ${cust.name}`}
                          >
                            <MessageCircle size={16} className="text-white" />
                            <span>Send Reminder</span>
                            <ArrowUpRight size={14} className="opacity-70" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* Table Footer info */}
          <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row sm:items-center sm:justify-between text-xs text-slate-500 gap-2">
            <span>
              Showing {filteredOverdue.length} of {overdueAccounts.length} overdue customer{overdueAccounts.length === 1 ? "" : "s"}
            </span>
            <span className="text-slate-400 italic">
              Clicking "Send Reminder" launches WhatsApp Web with the pre-filled template message.
            </span>
          </div>

        </section>

      </div>
    </div>
  );
}
