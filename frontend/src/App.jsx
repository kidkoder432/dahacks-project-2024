// src/Location.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Location() {
  const [locationData, setLocationData] = useState(null); // State to store response from backend
  const [error, setError] = useState(null); // State to store any error messages

  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          const timestamp = new Date().toISOString(); // Get current time in UTC (ISO format)
          sendLocation(latitude, longitude, timestamp);
        },
        (err) => setError("Error fetching location: " + err.message)
      );
    } else {
      setError("Geolocation not available");
    }
  }, []);

  const sendLocation = async (latitude, longitude, timestamp) => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/location', {
        latitude,
        longitude,
        timestamp, // Include UTC time in the payload
      });
      setLocationData(response.data); // Update locationData with response from backend
    } catch (err) {
      setError("Error sending location: " + err.message);
    }
  };

  return (
    <div>
      <h2>Location App</h2>
      {error ? (
        <p style={{ color: 'red' }}>{error}</p>
      ) : locationData ? (
        <div>
          <p><strong>Message:</strong> {locationData.message}</p>
          <p><strong>Latitude:</strong> {locationData.latitude}</p>
          <p><strong>Longitude:</strong> {locationData.longitude}</p>
          <p><strong>Timestamp (UTC):</strong> {locationData.timestamp}</p>
        </div>
      ) : (
        <p>Fetching location...</p>
      )}
    </div>
  );
}

export default Location;
