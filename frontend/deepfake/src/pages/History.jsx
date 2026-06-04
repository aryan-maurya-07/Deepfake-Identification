import React, { useEffect, useState } from "react";
import "./History.css";

export default function History({ user }) {
  const [uploads, setUploads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;

    const userId = user._id || user.id;

    fetch(`http://127.0.0.1:5000/results/${userId}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) setUploads(data.results || []);
        else setError("Failed to fetch history");
        setLoading(false);
      })
      .catch(() => {
        setError("Server error");
        setLoading(false);
      });
  }, [user]);

  if (!user)
    return <p style={{ color: "white", textAlign: "center" }}>Please login to view history.</p>;
  if (loading)
    return <p style={{ color: "white", textAlign: "center" }}>Loading...</p>;
  if (error)
    return <p style={{ color: "red", textAlign: "center" }}>{error}</p>;

  return (
    <div className="page history-page">
      <div className="container card">
        <h2>Upload History</h2>
        {uploads.length === 0 ? (
          <p>No uploads yet.</p>
        ) : (
          <table className="history-table">
            <thead>
              <tr>
                <th>File Name</th>
                <th>Result</th>
                <th>Confidence</th>
                <th>Uploaded At (IST)</th>
              </tr>
            </thead>
            <tbody>
              {uploads.map(u => {
                let uploadedAt = "N/A";
                if (u.created_at) {
                  // Convert UTC to IST by adding 5.5 hours
                  const utcTime = new Date(u.created_at);
                  const istTime = new Date(utcTime.getTime() + 5.5 * 60 * 60 * 1000);
                  uploadedAt = istTime.toLocaleString("en-IN", {
                    year: "numeric",
                    month: "short",
                    day: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: true
                  });
                }

                return (
                  <tr key={u._id || u.id}>
                    <td>{u.filename}</td>
                    <td>{u.result === "Fake" ? "❌ Deepfake" : "✅ Real"}</td>
                    <td>{(u.confidence * 100).toFixed(2)}%</td>
                    <td>{uploadedAt}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
