import React, { useEffect, useState } from "react";
import "./Dashboard.css";

export default function Dashboard({ user }) {
  const [stats, setStats] = useState({ total: 0, real: 0, deepfake: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;

    // Use MongoDB _id (ensure it's a string)
    const userId = user._id || user.id;

    fetch(`http://127.0.0.1:5000/results/${userId}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const uploads = data.results || [];
          const realCount = uploads.filter(u => u.result === "Real").length;
          const deepfakeCount = uploads.filter(u => u.result === "Fake").length;
          setStats({ total: uploads.length, real: realCount, deepfake: deepfakeCount });
        } else {
          setError("Failed to fetch stats");
        }
        setLoading(false);
      })
      .catch(() => {
        setError("Server error");
        setLoading(false);
      });
  }, [user]);

  if (!user)
    return <p style={{ color: "white", textAlign: "center" }}>Please login to view dashboard.</p>;
  if (loading)
    return <p style={{ color: "white", textAlign: "center" }}>Loading...</p>;
  if (error)
    return <p style={{ color: "red", textAlign: "center" }}>{error}</p>;

  return (
    <div className="page dashboard-page">
      <div className="container card">
        <h2>Dashboard</h2>
        <p>Total Uploads: {stats.total}</p>
        <p>✅ Real: {stats.real}</p>
        <p>❌ Deepfake: {stats.deepfake}</p>
      </div>
    </div>
  );
}
