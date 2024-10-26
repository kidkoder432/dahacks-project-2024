import React, {
    useRef,
    useEffect,
    useState,
    useImperativeHandle,
    forwardRef,
} from "react";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";
import Earth, { latLngToVector3 } from "./Earth"; 
import * as THREE from "three";

import axios from "axios";

const PORT = "http://127.0.0.1:5000";

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
    const [markerPosition, setMarkerPosition] = useState(null);

    const zoomToLocation = (lat, lng) => {
        const radius = 5;
        const targetPosition = latLngToVector3(lat, lng, radius + 2);
        targetRef.current.copy(targetPosition);
        setSpinning(false);
        camera.position.copy(
            targetPosition.clone().add(new THREE.Vector3(0, 0, 2))
        );
    };

    useImperativeHandle(ref, () => ({
        zoomToLocation,
        setMarkerPosition,
    }));

    useEffect(() => {
        zoomToLocation(40.7128, -74.006);
    }, []);

    useFrame(() => {
        camera.position.lerp(targetRef.current, 0.02);
        camera.lookAt(0, 0, 0);
    });

    return (
        <>
            <Earth spinning={spinning} />
            {markerPosition && <Marker position={markerPosition} />}
        </>
    );
});

function App() {
    const zoomableEarthRef = useRef();
    const [latLng, setLatLng] = useState(null);
    const [utcTime, setUtcTime] = useState(null);
    const [buttonVisible, setButtonVisible] = useState(true);
    const [error, setError] = useState(null);
    const [constellations, setConstellations] = useState([]);
    const [selectedConstellation, setSelectedConstellation] = useState(null);

    const getLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    let lng = position.coords.longitude;

                    lng += 3.5;

                    const markerPosition = latLngToVector3(lat, lng, 5);

                    zoomableEarthRef.current.setMarkerPosition(markerPosition);
                    zoomableEarthRef.current.zoomToLocation(lat, lng);

                    setLatLng({ latitude: lat, longitude: lng });
                    setUtcTime(new Date().toUTCString());
                    setButtonVisible(false);
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
    const zoomies = () => {
        zoomableEarthRef.current.zoomToLocation(0, 0);
    }
    

    const handleStarsInMyArea = async () => {
        console.log("Fetching stars in your area!");
        try {
            const response = await axios.post(PORT + "/visible", {
                latitude: latLng.latitude,
                longitude: latLng.longitude,
                timestamp: utcTime,
            });

            console.log("Stars fetched successfully:", response.data);

            setConstellations(response.data);
        } catch (err) {
            setError("Error sending location: " + err.message);
        }
    };

    const handleSendLocation = () => {
        if (constellations.length > 0) {
            const randomConstellation =
                constellations[
                    Math.floor(Math.random() * constellations.length)
                ];
            setSelectedConstellation(randomConstellation.constellation);
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

            {!constellations.length && (
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
                        height: "180px",
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
                        OnlyStars 💫
                    </h2>

                    {buttonVisible && (
                        <button
                            onClick={getLocation}
                            style={{
                                border: "none",
                                borderRadius: "5px",
                                backgroundColor: "rgba(255, 255, 255, 0.5)",
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
                            UTC Time: {utcTime}
                        </div>
                    )}

                    {latLng && (
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
            )}

            {constellations.length > 0 && !selectedConstellation && (
                <div
                    style={{
                        position: "absolute",
                        top: "50%",
                        left: "50%",
                        transform: "translate(-50%, -50%)",
                        color: "white",
                        borderRadius: "10px",
                        backgroundColor: "rgba(0, 0, 0, 0.3)",
                        padding: "15px",
                        display: "flex",
                        flexWrap: "wrap",
                        justifyContent: "center",
                        alignItems: "center",
                        animation: "rainbow-border 2s linear infinite",
                        border: "4px solid transparent",
                        width: "280px",
                        boxShadow: "0 0 15px rgba(355, 355, 355, 0.5)",
                    }}
                >
                    {constellations.map((constellation, index) => (
                        <div
                            key={index}
                            style={{
                                backgroundColor: "yellow",
                                color: "black",
                                padding: "5px",
                                borderRadius: "3px",
                                textAlign: "center",
                                fontSize: "14px",
                                margin: "5px",
                            }}
                        >
                            {constellation.constellation}
                        </div>
                    ))}

                    <button
                        onClick={handleSendLocation}
                        
                        style={{
                            border: "none",
                            borderRadius: "5px",
                            backgroundColor: "rgba(255, 255, 255, 0.5)",
                            color: "black",
                            padding: "5px 10px",
                            cursor: "pointer",
                            width: "100%",
                            marginTop: "10px",
                            fontSize: "16px",
                        }}
                    >
                        Find my lucky Star 🥰
                    </button>
                </div>
            )}

            {selectedConstellation && (
                <div
                    style={{
                        position: "absolute",
                        top: "50%",
                        left: "50%",
                        transform: "translate(-50%, -50%)",
                        color: "white",
                        borderRadius: "10px",
                        backgroundColor: "rgba(0, 0, 0, 0.3)",
                        padding: "15px",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        animation: "rainbow-border 2s linear infinite",
                        border: "4px solid transparent",
                        width: "280px",
                        boxShadow: "0 0 15px rgba(355, 355, 355, 0.5)",
                    }}
                >
                    <h2
                        style={{
                            margin: "0 0 20px 0",
                            textAlign: "center",
                            fontSize: "24px",
                        }}
                    >
                        Random Constellation
                    </h2>
                    <div
                        style={{
                            backgroundColor: "yellow",
                            color: "black",
                            padding: "10px",
                            borderRadius: "5px",
                            textAlign: "center",
                            fontSize: "20px",
                        }}
                    >
                        {selectedConstellation}
                    </div>
                </div>
            )}

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
