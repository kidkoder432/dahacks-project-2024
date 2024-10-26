// Earth.js
import React, { useRef, useEffect } from "react";
import { useTexture } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

function Earth({ spinning }) {
  const [colorMap, bumpMap, specularMap] = useTexture([
    process.env.PUBLIC_URL + "/textures/earthmap.jpg",
    process.env.PUBLIC_URL + "/textures/earthbump.jpg",
    process.env.PUBLIC_URL + "/textures/earthspec.jpg"
  ]);

  const earthRef = useRef();
  const sunLightRef = useRef();

  useEffect(() => {
    // Update the lighting when the component mounts
    updateLighting();
  }, []);

  useFrame((state, delta) => {
    if (earthRef.current && spinning) {
      earthRef.current.rotation.y += delta * 0.1;
    }
    updateLighting(); // Update lighting on each frame
  });

  const updateLighting = () => {
    const currentDate = new Date();
    const hours = currentDate.getUTCHours();
    const minutes = currentDate.getUTCMinutes();
    const totalMinutes = hours * 60 + minutes;

    // Determine the angle of the sun based on the current time (simplified)
    const sunAngle = (totalMinutes / (24 * 60)) * 2 * Math.PI; // Full rotation over 24 hours

    // Update the directional light's position and color based on the sun angle
    if (sunLightRef.current) {
      sunLightRef.current.position.set(
        Math.cos(sunAngle) * 10, // X position
        Math.sin(sunAngle) * 10, // Y position
        0 // Z position (assuming a flat light plane)
      );

      // Set the light color based on its position
      const color = sunLightRef.current.position.y > 0 ? 0xffffff : 0xaaaaaa; // White if above horizon, gray if below
      sunLightRef.current.color.set(color);
      sunLightRef.current.intensity = Math.max(0, sunLightRef.current.position.y / 10); // Adjust intensity based on height
    }
  };

  return (
    <>
      <directionalLight ref={sunLightRef} intensity={1} />
      <mesh ref={earthRef} rotation={[0, 0, 0]}>
        <sphereGeometry args={[5, 128, 128]} />
        <meshPhongMaterial
          map={colorMap}
          bumpMap={bumpMap}
          bumpScale={0.05}
          specularMap={specularMap}
          specular={new THREE.Color("white")}
          shininess={100000000000}
        />
      </mesh>
    </>
  );
}

export function latLngToVector3(lat, lng, radius = 9) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);

  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);

  return new THREE.Vector3(x, y, z);
}

export default Earth;

/*
// Earth.js
import React, { useRef } from "react";
import { useTexture } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

function Earth({ spinning }) { // Accept a spinning prop
  const [colorMap, bumpMap, specularMap] = useTexture([
    process.env.PUBLIC_URL + "/textures/earthmap.jpg",
    process.env.PUBLIC_URL + "/textures/earthbump.jpg",
    process.env.PUBLIC_URL + "/textures/earthspec.jpg"
  ]);

  const earthRef = useRef();

  useFrame((state, delta) => {
    if (earthRef.current && spinning) { // Rotate only if spinning is true
      earthRef.current.rotation.y += delta * 0.1;
    }
  });

  return (
    <mesh ref={earthRef} rotation={[0, 0, 0]}>
      <sphereGeometry args={[5, 128, 128]} />
      <meshPhongMaterial
        map={colorMap}
        bumpMap={bumpMap}
        bumpScale={0.05}
        specularMap={specularMap}
        specular={new THREE.Color("white")}
        shininess={100}
      />
    </mesh>
  );
}

export function latLngToVector3(lat, lng, radius = 9) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);

  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);

  return new THREE.Vector3(x, y, z);
}

export default Earth;

*/