import React from "react";
import "./Home.css";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="page home-page">
      <div className="hero">
        <h1>Deepfake Detection System</h1>
        <p>
          Upload images or videos to detect whether they are <span className="highlight">Real</span> or <span className="highlight">Deepfake</span>.
        </p>
        <div className="buttons">
          <Link to="/login" className="btn">Login</Link>
          <Link to="/signup" className="btn btn-outline">Signup</Link>
        </div>
      </div>
    </div>
  );
}
