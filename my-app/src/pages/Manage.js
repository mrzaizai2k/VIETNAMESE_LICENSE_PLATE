import React, { useEffect, useState } from "react";
import "./Manage.css";

const Manage = () => {
  const [records, setRecords] = useState([]);

  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem("records") || "[]");
    setRecords(saved);
  }, []);

  const moveRecord = (index, direction) => {
    const newRecords = [...records];
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= newRecords.length) return;
    [newRecords[index], newRecords[targetIndex]] = [
      newRecords[targetIndex],
      newRecords[index],
    ];
    setRecords(newRecords);
    localStorage.setItem("records", JSON.stringify(newRecords));
  };

  const deleteRecord = (index) => {
    const newRecords = records.filter((_, i) => i !== index);
    setRecords(newRecords);
    localStorage.setItem("records", JSON.stringify(newRecords));
  };

  const handleEdit = (index, newText) => {
    const newRecords = [...records];
    newRecords[index].text = newText;
    setRecords(newRecords);
    localStorage.setItem("records", JSON.stringify(newRecords));
  };

  return (
    <div className="manage-container">
      <h2>🗂 Manage Records</h2>

      {records.length === 0 ? (
        <p className="empty-msg">No records available.</p>
      ) : (
        <div className="record-grid">
          {records.map((rec, i) => (
            <div className="record-card" key={i}>
              {/* ✅ Show full frame image */}
              {rec.full_image ? (
                <img
                  src={rec.full_image}
                  alt={`Full Frame ${i}`}
                  className="record-image"
                />
              ) : rec.result_image ? (
                <img
                  src={rec.result_image}
                  alt={`Result ${i}`}
                  className="record-image"
                />
              ) : (
                <p className="no-image">No image available</p>
              )}

              <textarea
                value={rec.text}
                onChange={(e) => handleEdit(i, e.target.value)}
                className="record-text"
              />
              <p className="record-time">🕒 {rec.time}</p>
              <div className="record-actions">
                <button onClick={() => moveRecord(i, -1)}>⬆️</button>
                <button onClick={() => moveRecord(i, 1)}>⬇️</button>
                <button onClick={() => deleteRecord(i)}>🗑️</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Manage;
