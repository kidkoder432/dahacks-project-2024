import React, {
    useRef,
    useEffect,
    useState,
    useImperativeHandle,
    forwardRef,
} from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";
import Earth, { latLngToVector3 } from "./Earth"; // Ensure this imports your latLngToVector3 function
import * as THREE from "three";

import axios from "axios";
// Marker component
const Marker = ({ position }) => {
    return (
        <mesh position={position}>
            <sphereGeometry args={[0.02, 16, 16]} />
            <meshStandardMaterial color="red" />
        </mesh>
    );
};

const ZoomableEarth = forwardRef((_, ref) => {
    const { camera } = useThree();
    const targetRef = useRef(new THREE.Vector3());
    const [spinning, setSpinning] = useState(true);
    const [markerPosition, setMarkerPosition] = useState(null); // State to hold the marker position

    const zoomToLocation = (lat, lng) => {
        const radius = 5; // Ensure this matches your Earth sphere radius
        const targetPosition = latLngToVector3(lat, lng, radius + 2); // Offset for zoom
        targetRef.current.copy(targetPosition);
        setSpinning(false);

        // Set the camera position directly to the target position
        camera.position.copy(
            targetPosition.clone().add(new THREE.Vector3(0, 0, 2))
        ); // Adjust the camera position for a better view
    };

    useImperativeHandle(ref, () => ({
        zoomToLocation,
        setMarkerPosition, // Expose setMarkerPosition to update marker from App
    }));

    useEffect(() => {
        zoomToLocation(40.7128, -74.006); // Zoom to New York on mount
    }, []);

    useFrame(() => {
        camera.position.lerp(targetRef.current, 0.02);
        camera.lookAt(0, 0, 0);
    });

    return (
        <>
            <Earth spinning={spinning} />
            {markerPosition && <Marker position={markerPosition} />}{" "}
            {/* Render the marker if position is set */}
        </>
    );
});

function App() {
    const zoomableEarthRef = useRef();
    const [latLng, setLatLng] = useState(null); // State to hold latitude and longitude
    const [utcTime, setUtcTime] = useState(null); // State to hold UTC time
    const [buttonVisible, setButtonVisible] = useState(true); // State to control button visibility
    const [error, setError] = useState(null); // State to hold error message

    const getLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    let lng = position.coords.longitude;

                    // Adjust the longitude for offset to the right (e.g., +3.5 degrees)
                    lng += 3.5; // Change this value as needed to move the marker to the right

                    // Set the marker position in ZoomableEarth based on lat/lng
                    const markerPosition = latLngToVector3(lat, lng, 5); // Adjust radius as necessary

                    zoomableEarthRef.current.setMarkerPosition(markerPosition); // Update marker position
                    zoomableEarthRef.current.zoomToLocation(lat, lng); // Zoom to new location

                    // Set the latitude and longitude in state
                    setLatLng({ latitude: lat, longitude: lng });
                    setUtcTime(new Date().toUTCString()); // Get current UTC time
                    setButtonVisible(false); // Hide the button
                },
                (error) => {
                    console.error("Error obtaining location:", error);
                    alert(
                        "Unable to retrieve your location. Please allow location access."
                    );
                }
            );
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    };

    // Function to handle "Stars in my area" button click
    const handleStarsInMyArea = () => {
        console.log("Fetching stars in your area!"); // Replace with your actual logic to fetch stars
        try {
            const response = axios.post("http://127.0.0.1:5000/visible", {
                latitude: latLng.latitude,
                longitude: latLng.longitude,
                timestamp: utcTime,
            });

            console.log("Stars fetched successfully:", response.data);
            console.log("Constellation:", response.data.constellation);
            console.log("Magnitude:", response.data.magnitude);
            console.log("Altitude:", response.data.alt);
            console.log("Azimuth:", response.data.az);
            console.log("Time:", response.data.timestamp);
        } catch (err) {
            setError("Error sending location: " + err.message);
        }
    };

    return (
        <>
            <Canvas
                style={{ height: "100vh", background: "#000" }}
                camera={{ position: [0, 0, 15], fov: 75 }}
            >
                <ambientLight intensity={1.0} />
                <directionalLight position={[5, 10, 5]} intensity={1.0} />
                <Stars
                    radius={100}
                    depth={50}
                    count={5000}
                    factor={5}
                    saturation={0}
                    fade
                />
                <ZoomableEarth ref={zoomableEarthRef} />
                <OrbitControls enableZoom={true} />
            </Canvas>

            <div
                style={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                    color: "white",
                    borderRadius: "10px",
                    backgroundColor: "rgba(0, 0, 0, 0.3)",
                    padding: "20px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    animation: "rainbow-border 2s linear infinite",
                    border: "4px solid transparent",
                    width: "300px",
                    height: "180px", // Increased height for additional info
                    boxShadow: "0 0 15px rgba(355, 355, 355, 0.5)",
                }}
            >
                <h2
                    style={{
                        margin: "0 0 20px 0",
                        textAlign: "center",
                        fontSize: "28px",
                    }}
                >
                    OnlyStars
                </h2>

                {buttonVisible && ( // Render the button if it's visible
                    <button
                        onClick={getLocation}
                        style={{
                            border: "none",
                            borderRadius: "5px",
                            backgroundColor: "white",
                            color: "black",
                            padding: "5px 10px",
                            cursor: "pointer",
                            width: "100%",
                            marginBottom: "10px",
                            fontSize: "20px",
                        }}
                    >
                        Share my location 🤫
                    </button>
                )}

                {/* Display latitude and longitude if they are set */}
                {latLng && (
                    <div
                        style={{
                            textAlign: "center",
                            color: "white",
                            fontSize: "18px",
                            marginBottom: "10px",
                        }}
                    >
                        Latitude: {latLng.latitude.toFixed(4)}
                        <br />
                        Longitude: {latLng.longitude.toFixed(4)}
                        <br />
                        UTC Time: {utcTime} {/* Display UTC Time */}
                    </div>
                )}

                {/* "Stars in my area" button */}
                {latLng && ( // Only show this button if latLng is set
                    <button
                        onClick={handleStarsInMyArea}
                        style={{
                            border: "none",
                            borderRadius: "5px",
                            backgroundColor: "gold",
                            color: "black",
                            padding: "5px 10px",
                            cursor: "pointer",
                            width: "100%",
                            fontSize: "20px",
                        }}
                    >
                        Stars in my area 😈
                    </button>
                )}
            </div>

            {/* CSS for rainbow border animation */}
            <style>
                {`
          @keyframes rainbow-border {
            0% {
              border-color: red;
            }
            14% {
              border-color: orange;
            }
            28% {
              border-color: yellow;
            }
            42% {
              border-color: green;
            }
            57% {
              border-color: blue;
            }
            71% {
              border-color: indigo;
            }
            85% {
              border-color: violet;
            }
            100% {
              border-color: red;
            }
          }
        `}
            </style>
        </>
    );
}

export default App;

/*
import React, { useRef, useEffect, useState, useImperativeHandle, forwardRef } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Stars, Text } from "@react-three/drei";
import Earth, { latLngToVector3 } from "./Earth";
import * as THREE from "three";

const ZoomableEarth = forwardRef((_, ref) => {
  const { camera } = useThree();
  const targetRef = useRef(new THREE.Vector3());
  const [spinning, setSpinning] = useState(true); // State to control spinning

  const zoomToLocation = (lat, lng) => {
    const radius = 5; // Ensure this matches your Earth sphere radius
    const targetPosition = latLngToVector3(lat, lng, radius + 2); // Offset for zoom
    targetRef.current.copy(targetPosition);
    setSpinning(false);

    // Set the camera position directly to the target position
    camera.position.copy(targetPosition.clone().add(new THREE.Vector3(0, 0, 2))); // Adjust the camera position for a better view
  };

  useImperativeHandle(ref, () => ({
    zoomToLocation,
  }));

  useEffect(() => {
    zoomToLocation(40.7128, -74.0060); // Zoom to New York on mount
  }, []);

  useFrame(() => {
    camera.position.lerp(targetRef.current, 0.02);
    camera.lookAt(0, 0, 0);
  });

  return <Earth spinning={spinning} />; // Pass spinning state to Earth
});

function App() {
  const [latitude, setLatitude] = useState(0);
  const [longitude, setLongitude] = useState(0);
  const zoomableEarthRef = useRef();

  const handleZoom = (e) => {
    e.preventDefault();
    const lat = parseFloat(latitude);
    const lng = parseFloat(longitude);
    if (!isNaN(lat) && !isNaN(lng)) {
      // Call zoomToLocation with user input
      zoomableEarthRef.current.zoomToLocation(lat, lng);
    } else {
      alert("Please enter valid latitude and longitude values.");
    }
  };

  return (
    <>
      <Canvas style={{ height: "100vh", background: "#000" }} camera={{ position: [0, 0, 15], fov: 75 }}>
        <ambientLight intensity={1.0} />
        <directionalLight position={[5, 10, 5]} intensity={1.0} />
        <Stars radius={100} depth={50} count={5000} factor={5} saturation={0} fade />
        <ZoomableEarth ref={zoomableEarthRef} />
        <OrbitControls enableZoom={true} />
      </Canvas>

      <div style={{
        position: "absolute",
        top: 300,
        left: 550,
        color: "white",
        border: "2px solid white", // White border
        borderRadius: "10px", // Rounded edges
        backgroundColor: "rgba(255, 255, 255, 0.2)", // Transparent white background
        padding: "15px", // Padding inside the box
      }}>
        <h2 style={{ margin: "0 0 20px 0", textAlign: "center", fontSize: "24px" }}>OnlyStars</h2>
        
        <form onSubmit={handleZoom}>
          <input
            type="number"
            step="any"
            placeholder="Latitude"
            value={latitude}
            onChange={(e) => setLatitude(e.target.value)}
            style={{
              marginRight: 10,
              border: "1px solid white", // White border for input
              borderRadius: "5px", // Rounded edges for input
              backgroundColor: "transparent", // Transparent background
              color: "white", // White text
              padding: "5px", // Padding inside input
            }}
          />
          <input
            type="number"
            step="any"
            placeholder="Longitude"
            value={longitude}
            onChange={(e) => setLongitude(e.target.value)}
            style={{
              marginRight: 10,
              border: "1px solid white", // White border for input
              borderRadius: "5px", // Rounded edges for input
              backgroundColor: "transparent", // Transparent background
              color: "white", // White text
              padding: "5px", // Padding inside input
            }}
          />
          <button type="submit" style={{
            border: "none",
            borderRadius: "5px",
            backgroundColor: "white", // Button color
            color: "black", // Button text color
            padding: "5px 10px", // Padding for button
            cursor: "pointer",
          }}>
            Zoom
          </button>
        </form>
      </div>
    </>
  );
}

export default App;

*/
