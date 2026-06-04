import React from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";

export default function Navbar({ isLoggedIn, onLogout }) {
  return (
    <header className="navbar">
      <div className="nav-inner container">
        <Link to="/" className="brand">DeepAI</Link>
        <nav className="nav-links">
          {isLoggedIn && (
            <>
              <Link to="/dashboard" className="nav-link">Dashboard</Link>
              <Link to="/upload" className="nav-link">Upload</Link>
              <Link to="/history" className="nav-link">History</Link>
              <button className="nav-link btn-outline" onClick={onLogout}>Logout</button>
            </>
          )}
          {!isLoggedIn && (
            <>
              <Link to="/login" className="nav-link btn-outline">Login</Link>
              <Link to="/signup" className="nav-link btn-primary">Signup</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
