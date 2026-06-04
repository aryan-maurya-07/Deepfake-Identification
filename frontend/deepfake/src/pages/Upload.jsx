import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Upload.css';

export default function Upload({ user }) {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!user) {
      setError('Please login first to upload.');
      return;
    }

    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', user.id); // MongoDB user _id as string

    try {
      const res = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        setError(`Error: ${res.status} ${res.statusText}`);
        return;
      }

      let data;
      try {
        data = await res.json();
      } catch (err) {
        setError('Invalid response from server');
        return;
      }

      if (data.success) {
        navigate('/result', { state: data }); // Pass backend response to result page
      } else {
        setError(data.message || 'Upload failed');
      }
    } catch (err) {
      console.error(err);
      setError('Could not connect to server');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <p style={{ color: 'white', textAlign: 'center' }}>
        Please login first to upload.
      </p>
    );
  }

  return (
    <div className="page upload-page">
      <div className="container card">
        <h2>Upload File</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            accept="image/*,video/*"
          />
          <button
            type="submit"
            className="btn-primary"
            style={{ marginTop: '16px' }}
            disabled={loading}
          >
            {loading ? 'Uploading...' : 'Upload'}
          </button>
        </form>
        {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
      </div>
    </div>
  );
}

