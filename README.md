# Prototype Shifumi (Pierre-Feuille-Ciseaux) — Webcam + Hugging Face

Ce document contient un prototype complet (frontend + backend), les fichiers nécessaires, explications et étapes pour créer une application web qui :

* capture la main de l'utilisateur via la webcam
* envoie une image au backend
* le backend interroge un modèle sur Hugging Face (ou un endpoint d'inférence personnalisé)
* retourne la prédiction (pierre / feuille / ciseaux)
* calcule le gagnant contre un choix aléatoire du serveur

---

## Arborescence recommandée

```
shifumi-proto/
├─ frontend/                # app React simple (ou pure HTML/JS)
│  ├─ public/index.html
│  └─ src/
│     ├─ App.jsx
│     └─ index.jsx
├─ backend/
│  ├─ main.py               # FastAPI
│  ├─ model_client.py       # wrapper Hugging Face
│  └─ requirements.txt
├─ README.md
└─ .env.example
```

---

## 1) Pré-requis

* Node.js (v16+)
* Python 3.9+
* Un compte Hugging Face + clé d'API (HF_API_KEY)
* VSCode (tu l'as déjà)

Si tu n'as pas encore de modèle de reconnaissance de geste, tu peux :

* chercher un modèle déjà entraîné sur Hugging Face (image classification of hand gestures)
* ou entraîner un petit modèle (expliquer plus bas)

---

## 2) Backend (FastAPI)

Crée `backend/main.py` :

```python
# backend/main.py
# Serveur FastAPI simple qui reçoit une image base64, appelle HF et renvoie la prédiction

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import io
from PIL import Image
import random
from model_client import HFModelClient

app = FastAPI()

# Instancie le client HF (KEY via variable d'environnement)
hf = HFModelClient()

class PredictRequest(BaseModel):
    image_base64: str  # data URI ou base64 sans header

@app.post('/predict')
async def predict(req: PredictRequest):
    try:
        # retirer le préfixe data:image/png;base64, s'il existe
        b = req.image_base64
        if b.startswith('data:'):
            b = b.split(',', 1)[1]
        img_bytes = base64.b64decode(b)
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"image decode error: {e}")

    # Appel du modèle HF
    pred_label, score = hf.predict_image(img)

    # Serveur choisit un geste aléatoire
    choices = ['pierre', 'feuille', 'ciseaux']
    server_choice = random.choice(choices)

    # calcule le résultat
    result = compute_result(pred_label, server_choice)

    return {
        'user': pred_label,
        'score': float(score),
        'server': server_choice,
        'result': result
    }


def compute_result(user, server):
    if user == server:
        return 'egalite'
    wins = {
        'pierre': 'ciseaux',
        'ciseaux': 'feuille',
        'feuille': 'pierre'
    }
    if wins.get(user) == server:
        return 'gagne'
    else:
        return 'perdu'
```

**Annotations / explications :**

* On reçoit une image base64 depuis le front.
* `HFModelClient` contient la logique pour appeler l'API d'inférence (Hugging Face) — séparé pour faciliter les tests.

Crée `backend/model_client.py` :

```python
# backend/model_client.py
# Wrapper simple pour appeler l'API d'inference Hugging Face

import os
import io
import requests
from PIL import Image

HF_API_URL = os.getenv('HF_API_URL')  # ex: https://api-inference.huggingface.co/models/username/modelname
HF_API_KEY = os.getenv('HF_API_KEY')

class HFModelClient:
    def __init__(self):
        if not HF_API_URL or not HF_API_KEY:
            raise EnvironmentError('HF_API_URL et HF_API_KEY doivent être définis')
        self.url = HF_API_URL
        self.headers = {'Authorization': f'Bearer {HF_API_KEY}'}

    def predict_image(self, pil_image: Image.Image):
        # Convert image to bytes (PNG)
        buffered = io.BytesIO()
        pil_image.save(buffered, format='PNG')
        img_bytes = buffered.getvalue()

        # Appel à l'API d'inference
        response = requests.post(
            self.url,
            headers=self.headers,
            files={'file': ('image.png', img_bytes, 'image/png')},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        # Interprétation : dépend du modèle. Ex: output = [{'label': 'pierre', 'score': 0.86}, ...]
        if isinstance(data, list):
            top = max(data, key=lambda x: x.get('score', 0))
            return top.get('label'), top.get('score', 0)
        # Cas d'un endpoint personnalisé -> adapter ici
        raise ValueError('format de réponse HF inattendu: ' + str(data))
```

**requirements.txt** (backend) :

```
fastapi
uvicorn[standard]
pillow
requests
python-multipart
pydantic
```

---

## 3) Frontend (React minimal)

Voici un prototype React (Vite ou Create React App) qui :

* ouvre la webcam
* capture une image quand l'utilisateur clique sur "Jouer"
* envoie la photo encodée au backend
* affiche le résultat

Crée `frontend/src/App.jsx` :

```jsx
import React, {useRef, useEffect, useState} from 'react';

export default function App(){
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [status, setStatus] = useState('prêt');
  const [result, setResult] = useState(null);

  useEffect(()=>{
    async function start(){
      try{
        const stream = await navigator.mediaDevices.getUserMedia({video: true});
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }catch(e){
        setStatus('Erreur webcam: ' + e.message);
      }
    }
    start();
    return ()=>{
      // stop streams on unmount
      if(videoRef.current && videoRef.current.srcObject){
        videoRef.current.srcObject.getTracks().forEach(t=>t.stop());
      }
    }
  },[])

  async function captureAndSend(){
    setStatus('capture...');
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = 320;
    canvas.height = 240;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/png');

    setStatus('envoi au serveur...');
    try{
      const res = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({image_base64: dataUrl})
      });
      const j = await res.json();
      setResult(j);
      setStatus('prêt');
    }catch(e){
      setStatus('Erreur: ' + e.message);
    }
  }

  return (
    <div style={{fontFamily: 'sans-serif', padding: 20}}>
      <h1>Shifumi - Prototype</h1>
      <video ref={videoRef} style={{width: 320, height: 240, border: '1px solid #333'}} />
      <div style={{marginTop: 8}}>
        <button onClick={captureAndSend}>Jouer</button>
        <span style={{marginLeft:10}}>{status}</span>
      </div>
      <canvas ref={canvasRef} style={{display:'none'}} />

      {result && (
        <div style={{marginTop: 12}}>
          <div>Ton geste : <b>{result.user}</b> (confiance: {Math.round(result.score*100)}%)</div>
          <div>Serveur : <b>{result.server}</b></div>
          <div>Résultat : <b>{result.result}</b></div>
        </div>
      )}
    </div>
  );
}
```

Crée `frontend/src/index.jsx` :

```jsx
import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

createRoot(document.getElementById('root')).render(<App />)
```

`public/index.html` standard avec une div `root`.

**Remarques :**

* Le frontend capture `320x240` pour réduire la taille.
* En production, sécuriser les entêtes et utiliser HTTPS.

---

## 4) Variables d'environnement (.env)

Crée `.env` (ne pas pousser sur Git!) :

```
HF_API_URL=https://api-inference.huggingface.co/models/<ton-username>/<ton-modele>
HF_API_KEY=hf_xxxYOURKEYxxx
```

`HF_API_URL` : si tu as créé un `inference endpoint` (via Hugging Face Inference Endpoints) utilise l'URL fournie. Si tu utilises l'API public d'inference, le pattern ci-dessus fonctionne.

---

## 5) Étapes pour démarrer localement

1. Cloner ou créer le dossier selon l'arborescence.
2. Backend :

   * `cd backend`
   * `python -m venv .venv && source .venv/bin/activate` (ou `.venv\Scripts\activate` sous Windows)
   * `pip install -r requirements.txt`
   * définir les variables d'env (HF_API_URL et HF_API_KEY)
   * `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
3. Frontend :

   * `cd frontend`
   * `npm init vite@latest . --template react` (si tu veux vite) ou CRA
   * `npm install`
   * `npm run dev` (Vite) — ouvre le port indiqué (3000/5173 selon config)
4. Ouvre la page frontend, autorise la webcam, clique "Jouer".

---

## 6) Que faire si tu n'as pas de modèle prêt ?

* Option rapide : créer un *heuristic stub* sur le backend pendant le développement :

  * analyser l'image (ex: brightness/contours) et retourner aléatoirement "pierre/feuille/ciseaux" pour tester l'interface.
* Option meilleure : chercher sur Hugging Face un modèle de classification d'images qui reconnaît tes trois classes. Rechercher : "hand gestures", "rock paper scissors" ou "gesture recognition".
* Option entraînement : collecter ~300-1000 images par classe, fine-tune un modèle MobileNet ou ResNet via `transformers`/`datasets`/`accelerate` ou utiliser AutoTrain de Hugging Face.

---

## 7) Conseils d'amélioration

* Ajouter un flux temps-réel : websocket pour envoyer continuellement des frames et afficher animation.
* Prédiction locale (client) : si tu veux latence plus faible, convertir le modèle au format TensorFlow.js ou ONNX et l'exécuter dans le navigateur.
* UI/UX : ajouter compte à rebours, animation, détection de main (d'abord détecter qu'une main est présente avant de capturer).
* Robustesse : normaliser la taille et l'orientation de l'image, augmenter les données (data augmentation) pendant l'entraînement.

---

## 8) Dépannage courant

* `405 Method Not Allowed` : assure-toi que la route (POST /predict) est bien appelée et que l'URL correspond (http vs https, trailing slash). Vérifie CORS.
* CORS : si frontend et backend sont sur différents ports, ajoute `from fastapi.middleware.cors import CORSMiddleware` et autorise l'origine de dev.

Exemple CORS minimal à ajouter dans `main.py` :

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 9) Notes sur sécurité & coûts (Hugging Face)

* Les endpoints d'inference peuvent avoir un coût si tu utilises Inference Endpoints. Vérifie ton quota.
* Ne publie jamais ta clé `HF_API_KEY` dans un repo public.

---

## 10) Exemple de stub local (si pas de HF)

Remplace l'appel HF par :

```python
# stub: toujours renvoie 'pierre' avec score 0.9
return 'pierre', 0.9
```

---

## 11) Bonne pratique pour la formation d'un modèle (résumé rapide)

1. Collecte images (diverses mains, lumières, fonds) — au moins 300/ex classe.
2. Nettoyage & labelling.
3. Split train/val/test.
4. Fine-tune un modèle léger (MobileNet/efficientnet) en image classification.
5. Eval & export (TorchScript, ONNX, TF.js selon besoin).
6. Déployer (HF or local server).

---

## 12) FAQ rapide

**Q : Je veux que l'appli reconnaisse ma main en temps réel — est-ce possible ?**
R : Oui — exécute un modèle converti en TF.js/ONNX dans le navigateur, ou envoie frames régulièrement via websocket. Le trade-off est latence vs confidentialité.

**Q : Comment tester sans modèle ?**
R : Utilise le stub (voir section 10) pour simuler la réponse et tester l'UI.

---

