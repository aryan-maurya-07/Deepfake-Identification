
import React from 'react';
import { useLocation } from 'react-router-dom';
import './Result.css';

export default function Result() {
  const location = useLocation();
  const data = location.state;

  if (!data) 
    return <p style={{ color: 'white', textAlign: 'center' }}>No result to display</p>;

  // Convert confidence to percentage
  const confidencePercent = (data.confidence * 100).toFixed(2);

  return (
    <div className="page result-page">
      <div className="container card">
        <h2>Detection Result</h2>
        <div className="result-card">
          <div className="result-label">
            {data.result === 'Fake' ? '❌ Deepfake' : '✅ Real'}
          </div>
          <div className="result-confidence">
            Confidence: {confidencePercent}%
          </div>
        </div>
      </div>
    </div>
  );
}

