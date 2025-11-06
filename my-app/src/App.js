import React, { useState } from "react";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Inference from "./pages/Inference";
import Train from "./pages/Train";
import Manage from "./pages/Manage"; // NEW
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("Home");

  return (
    <div className="App">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      {activeTab === "Home" && <Home />}
      {activeTab === "Inference" && <Inference />}
      {activeTab === "Train" && <Train />}
      {activeTab === "Manage" && <Manage />}
    </div>
  );
}

export default App;
