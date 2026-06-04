import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Upload from "./pages/Upload";
import Result from "./pages/Result";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";

export default function App() {
  const [user, setUser] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // ✅ Load user from localStorage on refresh
  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogin = () => setIsLoggedIn(true);
  const handleLogout = () => {
    setIsLoggedIn(false);
    setUser(null);
    localStorage.removeItem("user");
  };

  return (
    <Router>
      <div className="app-root">
        <Navbar isLoggedIn={isLoggedIn} onLogout={handleLogout} />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login setUser={setUser} onLogin={handleLogin} />} />
            <Route path="/signup" element={<Signup />} />
            <Route
              path="/dashboard"
              element={isLoggedIn ? <Dashboard user={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/upload"
              element={isLoggedIn ? <Upload user={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/history"
              element={isLoggedIn ? <History user={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/result"
              element={isLoggedIn ? <Result user={user} /> : <Navigate to="/login" />}
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
