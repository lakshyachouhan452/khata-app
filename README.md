# 📒 Khata Book - Digital Shopkeeper Ledger

A full-stack digital ledger web application for shopkeepers built with **FastAPI**, **SQLAlchemy 2.0 (async)**, **PostgreSQL**, and **React (Vite)**.

---

## 🏗️ Project Architecture

```text
khata-app/
├── backend/                  # Python FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application instance & entry point
│   │   ├── api/              # API routers/endpoints (customers, transactions)
│   │   ├── core/             # Configuration, database setup, dependencies
│   │   ├── models/           # SQLAlchemy database models (Customer, Transaction)
│   │   ├── schemas/          # Pydantic models (data validation & serialization)
│   │   ├── services/         # Business logic (CustomerService, TransactionService, AnalyticsService)
│   │   └── tasks/            # Background notification & overdue scheduler jobs
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Backend environment variables
│
├── frontend/                 # React (Vite) Frontend
│   ├── src/
│   │   ├── assets/           # Images, icons
│   │   ├── components/       # Reusable UI parts (Navbar, KhataCard, Modals)
│   │   ├── pages/            # Page views (Dashboard, CustomerLedger)
│   │   ├── services/         # Axios API calls to FastAPI
│   │   ├── utils/            # Helper functions (currency formatters, date parsers)
│   │   ├── App.jsx           # Main React component
│   │   ├── main.jsx          # React entry point
│   │   └── index.css         # Modern, responsive UI design
│   ├── package.json          # Node dependencies
│   └── .env                  # Frontend environment variables (VITE_API_URL)
│
├── .gitignore
└── README.md
```

---

## ⚡ Features

1. **Customer Ledger Management**:
   - Customer profile creation with duplicate phone validation.
   - Real-time `total_outstanding` balance automatically kept up-to-date.
   - Full customer transaction history with cascade deletion.
2. **Double-Entry Style Shop Transactions**:
   - **Gave Credit (उधार दिया)**: Increases outstanding receivable balance.
   - **Received Payment (जमा मिला)**: Reduces outstanding receivable balance.
3. **Specialized Analytics Endpoints**:
   - `GET /api/v1/transactions/expected-in-next-7-days`: Aggregates upcoming credit collections due within 7 days.
   - `GET /api/v1/customers/overdue`: Pinpoints customers with unpaid or expired due dates.
4. **Background Tasks**:
   - Scheduled periodic task in `tasks/scheduler.py` that checks for expired due dates and updates transaction status to `overdue`.
5. **Interactive UI**:
   - Live dashboard cards (Total Outstanding, Next 7 Days expected, Overdue accounts).
   - Filter by customer name/phone.
   - Dedicated customer ledger modal for recording credit and payments with status flags and due dates.

---

## 🚀 Getting Started

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend Setup

```bash
cd frontend

# Install npm packages
npm install

# Start Vite dev server
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.
