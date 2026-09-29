import React from "react";
import { BookOpen, Users, PlusCircle } from "lucide-react";

export default function Navbar({ activeTab, setActiveTab, onOpenNewCustomer }) {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div
          className="flex items-center gap-3 cursor-pointer group"
          onClick={() => setActiveTab("dashboard")}
        >
          <div className="w-10 h-10 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <BookOpen size={22} />
          </div>
          <div>
            <div className="font-bold text-slate-900 leading-tight tracking-tight text-lg">
              Khata Book
            </div>
            <div className="text-xs text-slate-500 font-medium">
              Digital Shopkeeper Ledger
            </div>
          </div>
        </div>

        {/* Navigation & Action */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === "dashboard"
                ? "bg-blue-50 text-blue-700 font-semibold"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            }`}
          >
            Dashboard
          </button>

          <button
            onClick={onOpenNewCustomer}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm hover:shadow transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
          >
            <PlusCircle size={17} />
            <span>Add Customer</span>
          </button>
        </div>
      </div>
    </header>
  );
}
