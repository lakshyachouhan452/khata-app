import React, { useState } from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import CustomerModal from "./components/CustomerModal";
import { createCustomer } from "./services/api";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [isAddCustomerOpen, setIsAddCustomerOpen] = useState(false);

  const handleCreateCustomer = async (data) => {
    await createCustomer(data);
    // Reload or refresh state
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenNewCustomer={() => setIsAddCustomerOpen(true)}
      />

      <main className="flex-1">
        <Dashboard onOpenAddCustomer={() => setIsAddCustomerOpen(true)} />
      </main>

      <CustomerModal
        isOpen={isAddCustomerOpen}
        onClose={() => setIsAddCustomerOpen(false)}
        onSave={handleCreateCustomer}
      />
    </div>
  );
}
