import React, { useState } from "react";
import axios from "axios";
import "./Train.css";

const Train = () => {
  const [images, setImages] = useState([]);
  const [training, setTraining] = useState(false);
  const [message, setMessage] = useState("");

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
      e.target.value = ""; // reset input for same file re-upload
    });
  };

  // Label editing
  const handleLabelChange = (index, value) => {
    const updated = [...images];
    updated[index].label = value.toUpperCase();
    setImages(updated);
  };

  // Remove single image
  const removeImage = (index) => {
    const updated = [...images];
    updated.splice(index, 1);
    setImages(updated);
  };

  // Send all labeled images to backend
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
      const response = await axios.post("http://localhost:8000/train/", {
        data: images,
      });
      if (response.data.status === "ok") {
        setMessage("✅ Training completed successfully!");
        setImages([]); // 🔄 reset images for next batch
      } else {
        setMessage("❌ Training failed.");
      }
    } catch (err) {
      setMessage("🚨 Error: " + err.message);
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="train-container">
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
                className="remove-btn"
                onClick={() => removeImage(index)}
              >
                ✖
              </button>
            </div>
          ))}
        </div>
      )}

      <button
        onClick={handleTrain}
        className="train-btn"
        disabled={training}
      >
        {training ? "Training..." : "💾 Save & Train"}
      </button>

      {message && <p className="train-msg">{message}</p>}
    </div>
  );
};

export default Train;
