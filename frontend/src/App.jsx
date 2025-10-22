import React, { useRef, useEffect, useState } from "react";

export default function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [status, setStatus] = useState("Prêt");
  const [result, setResult] = useState(null);

  useEffect(() => {
    async function startWebcam() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      } catch (e) {
        setStatus("Erreur webcam: " + e.message);
      }
    }
    startWebcam();

    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  async function captureAndSend() {
    setStatus("Capture...");
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = 320;
    canvas.height = 240;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/png");

    setStatus("Envoi au serveur...");
    try {
      const res = await fetch("http://localhost:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_base64: dataUrl }),
      });
      const json = await res.json();
      setResult(json);
      setStatus("Prêt");
    } catch (e) {
      setStatus("Erreur: " + e.message);
    }
  }

  return (
    <div style={{ padding: 20, fontFamily: "sans-serif" }}>
      <h1>Shifumi AI</h1>
      <video
        ref={videoRef}
        style={{ width: 320, height: 240, border: "1px solid #333" }}
      />
      <div style={{ marginTop: 8 }}>
        <button onClick={captureAndSend}>Jouer</button>
        <span style={{ marginLeft: 10 }}>{status}</span>
      </div>
      <canvas ref={canvasRef} style={{ display: "none" }} />
      {result && (
        <div style={{ marginTop: 12 }}>
          <div>Ton geste : <b>{result.user}</b> (confiance : {Math.round(result.score * 100)}%)</div>
          <div>Serveur : <b>{result.server}</b></div>
          <div>Résultat : <b>{result.result}</b></div>
        </div>
      )}
    </div>
  );
}
