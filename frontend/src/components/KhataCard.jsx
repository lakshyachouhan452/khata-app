import React from "react";

export default function KhataCard({ title, amount, subtitle, icon: Icon, variant = "default" }) {
  return (
    <div className={`khata-card khata-card-${variant}`}>
      <div className="card-header">
        <span className="card-title">{title}</span>
        {Icon && (
          <div className="card-icon">
            <Icon size={20} />
          </div>
        )}
      </div>
      <div className="card-body">
        <h3 className="card-amount">{amount}</h3>
        {subtitle && <p className="card-subtitle">{subtitle}</p>}
      </div>
    </div>
  );
}
