
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

/*
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
          
          {locationData.constellations && (
            <div>
              <h3>Visible Constellations</h3>
              <ul>
                {locationData.constellations.map((constellation, index) => (
                  <li key={index} style={{ marginBottom: '20px' }}>
                    <strong>{constellation.name}</strong>
                    <p>{constellation.description}</p>
                    <p><strong>Best Viewing Time:</strong> {constellation.best_viewing_time}</p>
                    {constellation.image_url && (
                      <img src={constellation.image_url} alt={constellation.name} style={{ width: '150px', height: 'auto' }} />
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <p>Fetching location...</p>
      )}
      {locationData.constellations && locationData.constellations.length > 0 ? (
    <div>
      <h3>Visible Constellations</h3>
      <ul>
        {locationData.constellations.map((constellation, index) => (
          <li key={index} style={{ marginBottom: '20px' }}>
            <strong>{constellation.name}</strong>
            <p>{constellation.description}</p>
            <p><strong>Best Viewing Time:</strong> {constellation.best_viewing_time}</p>
            {constellation.image_url && (
              <img src={constellation.image_url} alt={constellation.name} style={{ width: '150px', height: 'auto' }} />
            )}
          </li>
        ))}
      </ul>
    </div>
) : (
    <p>No constellations visible at this time and location.</p>
)}
    </div>
  );
}

export default Location;
*/
