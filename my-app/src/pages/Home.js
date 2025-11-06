import React from "react";
import "./Home.css";

const Home = () => {
  return (
    <div className="home-container">
      <div className="hero-section">
        <div className="icon">🔍</div>
        <h1>License Plate Recognition</h1>
        <p className="course">
          Dự án môn: <span>Hệ thống thông minh</span>
        </p>

        <div className="students">
          <p>Sinh viên:</p>
          <ul>
            <li>Mai Chí Bảo</li>
            <li>Nguyễn Hoàng Long</li>
            <li>Huỳnh Nhật Anh</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Home;
