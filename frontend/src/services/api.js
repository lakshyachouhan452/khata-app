import axios from "axios";

// Base URL points to FastAPI backend running at http://localhost:8000
const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

/**
 * 1. Fetch all customers (can be used to calculate Total Outstanding)
 */
export const getCustomers = async (search = "") => {
  const params = search ? { search } : {};
  const response = await apiClient.get("/customers/", { params });
  return response.data;
};

/**
 * 2. Fetch single customer details with transactions
 */
export const getCustomerById = async (customerId) => {
  const response = await apiClient.get(`/customers/${customerId}`);
  return response.data;
};

/**
 * 3. Create a new customer
 */
export const createCustomer = async (customerData) => {
  const response = await apiClient.post("/customers/", customerData);
  return response.data;
};

/**
 * 4. Fetch the total credit amount expected in the next 7 days
 */
export const getExpectedNextWeek = async () => {
  const response = await apiClient.get("/transactions/expected-in-next-7-days");
  return response.data;
};

/**
 * 5. Fetch all customers with an overdue balance / overdue transactions
 */
export const getOverdueCustomers = async () => {
  const response = await apiClient.get("/customers/overdue");
  return response.data;
};

/**
 * 6. Record a transaction (gave_credit / received_payment)
 */
export const createTransaction = async (transactionData) => {
  const response = await apiClient.post("/transactions/", transactionData);
  return response.data;
};

/**
 * Helper to construct the WhatsApp reminder link.
 * Format: https://wa.me/{phone_number}?text=Hello {name}, your payment of {amount} is overdue.
 */
export const generateWhatsAppReminderLink = (phoneNumber, name, amount) => {
  // Strip non-numeric characters for the wa.me path
  const sanitizedPhone = String(phoneNumber || "").replace(/[^0-9]/g, "");
  const message = `Hello ${name}, your payment of ${amount} is overdue.`;
  return `https://wa.me/${sanitizedPhone}?text=${encodeURIComponent(message)}`;
};

export default apiClient;
