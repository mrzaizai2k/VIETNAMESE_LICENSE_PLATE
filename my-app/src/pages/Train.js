import React, { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from "recharts";
import "./Train.css";

const API_BASE = "http://localhost:8000";

const TrainWithBackend = () => {
  const [activeTab, setActiveTab] = useState("train");
  const [images, setImages] = useState([]);
  const [training, setTraining] = useState(false);
  const [message, setMessage] = useState("");
  const [trainingInfo, setTrainingInfo] = useState({ samples: 0, images: 0 });
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [kValueComparison, setKValueComparison] = useState([]);

  // Fetch config and training info on mount
  useEffect(() => {
    fetchConfig();
    fetchTrainingInfo();
    fetchEvaluation();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await fetch(`${API_BASE}/config/`);
      const data = await response.json();
      if (data.status === "ok") {
        setConfig(data.config);
      }
    } catch (error) {
      setMessage("⚠️ Failed to load configuration");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEvaluation = async () => {
    try {
      const response = await fetch(`${API_BASE}/evaluate/`);
      const data = await response.json();
      if (data.status === "ok") {
        const perfData = data.results?.map((item) => ({
          k: item.k,
          accuracy: parseFloat(item.accuracy),
          precision: parseFloat(item.precision),
          recall: parseFloat(item.recall),
          f1Score: parseFloat(item.f1),
        }));
        setKValueComparison(perfData || []);
      }
    } catch (error) {
      console.error("Failed to fetch evaluation:", error);
    }
  };

  const fetchTrainingInfo = async () => {
    try {
      const response = await fetch(`${API_BASE}/training-info/`);
      const data = await response.json();
      if (data.status === "ok") {
        setTrainingInfo({ samples: data.samples, images: data.images });
      }
    } catch (error) {
      console.error("Failed to fetch training info:", error);
    }
  };

  // Handle multi-file upload
  const handleUpload = (e) => {
    const files = Array.from(e.target.files);
    const newImages = files.map((file) => {
      const reader = new FileReader();
      return new Promise((resolve) => {
        reader.onload = () =>
          resolve({ image_base64: reader.result, label: "" });
        reader.readAsDataURL(file);
      });
    });
    Promise.all(newImages).then((loaded) => {
      setImages((prev) => [...prev, ...loaded]);
      e.target.value = "";
    });
  };

  const handleLabelChange = (index, value) => {
    const updated = [...images];
    updated[index].label = value.toUpperCase();
    setImages(updated);
  };

  const removeImage = (index) => {
    const updated = [...images];
    updated.splice(index, 1);
    setImages(updated);
  };

  const handleTrain = async () => {
    if (images.length === 0) {
      setMessage("⚠️ Please upload and label images first.");
      return;
    }
    if (images.some((img) => !img.label.trim())) {
      setMessage("⚠️ All images must have labels!");
      return;
    }

    setTraining(true);
    setMessage("⏳ Training in progress...");

    try {
      const response = await fetch(`${API_BASE}/train/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: images })
      });

      const result = await response.json();
      
      if (result.status === "ok") {
        setMessage("✅ Training completed successfully!");
        setImages([]);
        await fetchTrainingInfo();
        await fetchEvaluation(); // Refresh metrics after training
      } else {
        setMessage(`⚠️ Training failed: ${result.message || "Unknown error"}`);
      }
    } catch (error) {
      setMessage("⚠️ Failed to connect to backend");
      console.error(error);
    } finally {
      setTraining(false);
    }
  };

  // Configuration handlers
  const handleConfigChange = (section, key, value, index = null) => {
    setConfig(prev => {
      const newConfig = JSON.parse(JSON.stringify(prev));
      if (index !== null) {
        newConfig[section][key][index] = parseInt(value) || 0;
      } else {
        const parsedValue = parseFloat(value);
        newConfig[section][key] = isNaN(parsedValue) ? (parseInt(value) || value) : parsedValue;
      }
      return newConfig;
    });
  };

  const saveConfig = async () => {
    try {
      const response = await fetch(`${API_BASE}/config/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: config })
      });

      const result = await response.json();
      
      if (result.status === "ok") {
        setMessage("✅ Configuration saved successfully!");
        setConfig(result.updated);
      } else {
        setMessage(`⚠️ Failed to save: ${result.message}`);
      }
    } catch (error) {
      setMessage("⚠️ Failed to connect to backend");
      console.error(error);
    }
    
    setTimeout(() => setMessage(""), 3000);
  };

  if (loading || !config) {
    return (
      <div className="loading-container">
        Loading...
      </div>
    );
  }

  return (
    <div className="train-app">
      {/* Sidebar */}
      <div className="sidebar">
        <h2 className="sidebar-title">
          🎯 KNN Trainer
        </h2>
        
        <div className="sidebar-nav">
          <button
            onClick={() => setActiveTab("train")}
            className={`nav-btn ${activeTab === "train" ? "active" : ""}`}
          >
            🧠 Train Model
          </button>
          
          <button
            onClick={() => setActiveTab("config")}
            className={`nav-btn ${activeTab === "config" ? "active" : ""}`}
          >
            ⚙️ Configuration
          </button>
          
          <button
            onClick={() => setActiveTab("metrics")}
            className={`nav-btn ${activeTab === "metrics" ? "active" : ""}`}
          >
            📊 Metrics
          </button>
        </div>

        <div className="sample-counter">
          <div className="counter-value">
            {trainingInfo.samples}
          </div>
          <div className="counter-label">
            Training Samples
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Train Tab */}
        {activeTab === "train" && (
          <div className="train-tab">
            <h2>🧠 Train Model</h2>
            <p>Upload character images, label them, and train your model.</p>

            <input
              type="file"
              multiple
              accept="image/*"
              onChange={handleUpload}
              className="file-input"
            />

            {images.length === 0 ? (
              <p className="empty-msg">No images uploaded yet.</p>
            ) : (
              <div className="image-grid">
                {images.map((item, index) => (
                  <div key={index} className="image-card">
                    <img
                      src={item.image_base64}
                      alt={`uploaded-${index}`}
                      className="preview-img"
                    />
                    <input
                      type="text"
                      placeholder="Label (A-Z, 0-9)"
                      maxLength="1"
                      value={item.label}
                      onChange={(e) => handleLabelChange(index, e.target.value)}
                      className="label-input"
                    />
                    <button
                      onClick={() => removeImage(index)}
                      className="remove-btn"
                    >
                      ✖
                    </button>
                  </div>
                ))}
              </div>
            )}

            <button
              onClick={handleTrain}
              disabled={training}
              className={`train-btn ${training ? "disabled" : ""}`}
            >
              {training ? "Training..." : "💾 Save & Train"}
            </button>

            {message && <p className="train-msg">{message}</p>}
          </div>
        )}

        {/* Config Tab */}
        {activeTab === "config" && (
          <div className="config-tab">
            <h2>⚙️ Configuration</h2>
            <p className="config-description">
              Adjust preprocessing and model parameters
            </p>

            {/* Preprocess Section */}
            <div className="config-section">
              <h3 className="section-title">Preprocessing</h3>
              
              <div className="config-field">
                <label className="field-label">
                  Gaussian Smooth Filter Size
                </label>
                <div className="dual-input">
                  <input
                    type="number"
                    value={config.preprocess.GAUSSIAN_SMOOTH_FILTER_SIZE[0]}
                    onChange={(e) => handleConfigChange("preprocess", "GAUSSIAN_SMOOTH_FILTER_SIZE", e.target.value, 0)}
                    className="config-input"
                  />
                  <input
                    type="number"
                    value={config.preprocess.GAUSSIAN_SMOOTH_FILTER_SIZE[1]}
                    onChange={(e) => handleConfigChange("preprocess", "GAUSSIAN_SMOOTH_FILTER_SIZE", e.target.value, 1)}
                    className="config-input"
                  />
                </div>
              </div>

              <div className="config-field">
                <label className="field-label">
                  Adaptive Threshold Block Size
                </label>
                <input
                  type="number"
                  value={config.preprocess.ADAPTIVE_THRESH_BLOCK_SIZE}
                  onChange={(e) => handleConfigChange("preprocess", "ADAPTIVE_THRESH_BLOCK_SIZE", e.target.value)}
                  className="config-input full-width"
                />
              </div>

              <div className="config-field">
                <label className="field-label">
                  Adaptive Threshold Weight
                </label>
                <input
                  type="number"
                  value={config.preprocess.ADAPTIVE_THRESH_WEIGHT}
                  onChange={(e) => handleConfigChange("preprocess", "ADAPTIVE_THRESH_WEIGHT", e.target.value)}
                  className="config-input full-width"
                />
              </div>
            </div>

            {/* Image Section */}
            <div className="config-section">
              <h3 className="section-title">Image Settings</h3>
              
              <div className="config-field">
                <label className="field-label">
                  Resize Dimensions
                </label>
                <div className="dual-input">
                  <input
                    type="number"
                    value={config.image.resize[0]}
                    onChange={(e) => handleConfigChange("image", "resize", e.target.value, 0)}
                    placeholder="Width"
                    className="config-input"
                  />
                  <input
                    type="number"
                    value={config.image.resize[1]}
                    onChange={(e) => handleConfigChange("image", "resize", e.target.value, 1)}
                    placeholder="Height"
                    className="config-input"
                  />
                </div>
              </div>
            </div>

            {/* Plate Section */}
            <div className="config-section">
              <h3 className="section-title">Plate Detection</h3>
              
              <div className="grid-2">
                <div className="config-field">
                  <label className="field-label">
                    Min Char
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={config.plate.Min_char}
                    onChange={(e) => handleConfigChange("plate", "Min_char", e.target.value)}
                    className="config-input full-width"
                  />
                </div>
                <div className="config-field">
                  <label className="field-label">
                    Max Char
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={config.plate.Max_char}
                    onChange={(e) => handleConfigChange("plate", "Max_char", e.target.value)}
                    className="config-input full-width"
                  />
                </div>
                <div className="config-field">
                  <label className="field-label">
                    Resized Width
                  </label>
                  <input
                    type="number"
                    value={config.plate.RESIZED_IMAGE_WIDTH}
                    onChange={(e) => handleConfigChange("plate", "RESIZED_IMAGE_WIDTH", e.target.value)}
                    className="config-input full-width"
                  />
                </div>
                <div className="config-field">
                  <label className="field-label">
                    Resized Height
                  </label>
                  <input
                    type="number"
                    value={config.plate.RESIZED_IMAGE_HEIGHT}
                    onChange={(e) => handleConfigChange("plate", "RESIZED_IMAGE_HEIGHT", e.target.value)}
                    className="config-input full-width"
                  />
                </div>
              </div>
            </div>

            {/* Model Section */}
            <div className="config-section">
              <h3 className="section-title">Model Parameters</h3>
              
              <div className="config-field">
                <label className="field-label">
                  K Value (Number of Neighbors)
                </label>
                <input
                  type="number"
                  value={config.model.k_value}
                  onChange={(e) => handleConfigChange("model", "k_value", e.target.value)}
                  className="config-input full-width"
                />
              </div>
            </div>

            <button
              onClick={saveConfig}
              className="save-config-btn"
            >
              💾 Save Configuration
            </button>

            {message && <p className="config-msg">{message}</p>}
          </div>
        )}

        {/* Metrics Tab */}
        {activeTab === "metrics" && (
          <div className="metrics-tab">
            <h2>📊 KNN Performance Metrics</h2>
            <p className="metrics-description">
              Training performance analysis with {trainingInfo.samples} samples
            </p>

            {/* K-Value Comparison */}
            <div className="chart-container">
              <h3 className="chart-title">
                K-Value Performance Comparison
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={kValueComparison}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis 
                    dataKey="k" 
                    stroke="#aaa"
                    label={{ value: 'K Value', position: 'insideBottom', offset: -5, fill: '#aaa' }}
                  />
                  <YAxis 
                    stroke="#aaa"
                    label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft', fill: '#aaa' }}
                  />
                  <Tooltip 
                    formatter={(value) => `${(value * 100).toFixed(2)}%`}
                    contentStyle={{ 
                      background: 'rgba(10, 15, 31, 0.95)', 
                      border: '1px solid rgba(0, 194, 255, 0.3)',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Bar dataKey="accuracy" fill="#00c2ff" name="Accuracy (%)" />
                </BarChart>
              </ResponsiveContainer>
              <p className="k-value-info">
                Current K-value: <span className="highlight">{config.model.k_value}</span>
                {" "}(Accuracy: {kValueComparison.find(k => k.k === config.model.k_value) ? 
                    (kValueComparison.find(k => k.k === config.model.k_value).accuracy * 100).toFixed(2) 
                    : "N/A"}%)
              </p>
            </div>

            {/* Metrics Summary Cards */}
            <div className="metrics-grid">
              {kValueComparison.length > 0 ? (
                <>
                  <div className="metric-card accuracy">
                    <div className="metric-value">
                      {(kValueComparison.find(k => k.k === config.model.k_value)?.accuracy * 100 || 0).toFixed(2)}%
                    </div>
                    <div className="metric-label">Accuracy</div>
                  </div>

                  <div className="metric-card precision">
                    <div className="metric-value">
                      {(kValueComparison.find(k => k.k === config.model.k_value)?.precision * 100 || 0).toFixed(2)}%
                    </div>
                    <div className="metric-label">Precision</div>
                  </div>

                  <div className="metric-card recall">
                    <div className="metric-value">
                      {(kValueComparison.find(k => k.k === config.model.k_value)?.recall * 100 || 0).toFixed(2)}%
                    </div>
                    <div className="metric-label">Recall</div>
                  </div>

                  <div className="metric-card f1">
                    <div className="metric-value">
                      {(kValueComparison.find(k => k.k === config.model.k_value)?.f1Score * 100 || 0).toFixed(2)}%
                    </div>
                    <div className="metric-label">F1 Score</div>
                  </div>
                </>
              ) : (
                <p>No evaluation data yet. Run training first.</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrainWithBackend;
