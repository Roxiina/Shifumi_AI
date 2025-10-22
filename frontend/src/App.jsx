import React, { useRef, useEffect, useState } from "react";

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [result, setResult] = useState("");

  // Démarrer la caméra
  useEffect(() => {
    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Erreur caméra :", err);
      }
    }
    startCamera();
  }, []);

  // Capture l'image et envoie au backend
  const handlePlay = async () => {
    if (!videoRef.current) return;

    // On dessine la frame sur le canvas
    const canvas = canvasRef.current;
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    // Convertit en base64
    const imageBase64 = canvas.toDataURL("image/png");

    try {
      const res = await fetch("http://127.0.0.1:8000/jouer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ image: imageBase64 }),
      });

      if (!res.ok) throw new Error("Erreur backend");

      const data = await res.json();
      setResult(data.choice); // 'Pierre', 'Feuille' ou 'Ciseaux'
    } catch (err) {
      console.error(err);
      setResult("Erreur lors de la détection");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Shifumi AI</h1>
      <video
        ref={videoRef}
        autoPlay
        style={{ width: "400px", height: "300px", border: "2px solid black" }}
      />
      <br />
      <button onClick={handlePlay} style={{ marginTop: "20px", padding: "10px 20px" }}>
        Jouer
      </button>
      <p style={{ marginTop: "20px", fontSize: "24px" }}>{result}</p>
      <canvas ref={canvasRef} style={{ display: "none" }} />
    </div>
  );
}

export default App;
