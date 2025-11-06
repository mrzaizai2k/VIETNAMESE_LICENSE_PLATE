import React from "react";
import "./Navbar.css";

const Navbar = ({ activeTab, setActiveTab }) => {
  // ✅ Added "Manage" to the list
  const tabs = ["Home", "Inference", "Train", "Manage"];

  return (
    <div className="navbar">
      {tabs.map((tab) => (
        <button
          key={tab}
          className={activeTab === tab ? "active" : ""}
          onClick={() => setActiveTab(tab)}
        >
          {tab}
        </button>
      ))}
    </div>
  );
};

export default Navbar;
