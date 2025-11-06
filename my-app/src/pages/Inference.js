import React, { useState, useRef } from "react";
import axios from "axios";
import "./Inference.css";

const Inference = () => {
  const [videoFile, setVideoFile] = useState(null);
  const [result, setResult] = useState(null);
  const [timestamp, setTimestamp] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const handleFileChange = (e) => {
    setVideoFile(URL.createObjectURL(e.target.files[0]));
    setResult(null);
    setTimestamp(null);
  };

  const captureFrame = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    // Capture full frame
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const fullFrameBase64 = canvas.toDataURL("image/jpeg");

    try {
      const res = await axios.post("http://localhost:8000/recognize/", {
        image_base64: fullFrameBase64,
      });

      // Format timestamp
      const now = new Date();
      const formattedTime = now.toLocaleString("vi-VN", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });

      if (res.data.status === "ok" && res.data.results.length > 0) {
        const resultData = res.data.results[0];

        // Store both images: full frame + processed result
        const newRecord = {
          text: resultData.text,
          time: formattedTime,
          full_image: fullFrameBase64, // full captured frame
          result_image: resultData.image, // cropped or processed result from backend
        };

        // Save to localStorage
        const savedData = JSON.parse(localStorage.getItem("records") || "[]");
        savedData.push(newRecord);
        localStorage.setItem("records", JSON.stringify(savedData));

        setResult(resultData);
      } else {
        setResult({ text: "No plate detected", image: null });
      }

      setTimestamp(formattedTime);
    } catch (err) {
      console.error(err);
      setResult({ text: "Error recognizing plate", image: null });
      setTimestamp(null);
    }
  };

  return (
    <div className="inference-container">
      <h2>🎥 License Plate Recognition</h2>

      <input
        type="file"
        accept="video/mp4"
        onChange={handleFileChange}
        className="file-input"
      />

      {videoFile && (
        <div className="inference-content">
          {/* LEFT: Video + Capture button */}
          <div className="video-section">
            <video ref={videoRef} src={videoFile} controls width="640" />
            <canvas
              ref={canvasRef}
              width="640"
              height="360"
              style={{ display: "none" }}
            />
            <button onClick={captureFrame}>🔍 Recognize</button>
          </div>

          {/* RIGHT: Result */}
          {result && (
            <div className="result-section">
              <p className="result-text">
                <b>Result:</b> {result.text}
              </p>
              {timestamp && <p className="result-time">🕒 {timestamp}</p>}
              {result.image && (
                <img
                  src={result.image}
                  alt="Detected Plate"
                  className="result-image"
                />
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Inference;
