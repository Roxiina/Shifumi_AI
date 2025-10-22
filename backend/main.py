from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
from io import BytesIO
from PIL import Image

# Modèle attendu
class ImageInput(BaseModel):
    image: str

app = FastAPI()

# Autoriser ton frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/jouer")
async def jouer(input: ImageInput):
    try:
        # Décoder l'image Base64 envoyée depuis le frontend
        header, encoded = input.image.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        img = Image.open(BytesIO(img_bytes))
        
        # Ici tu appelles ton modèle YOLO/IA pour deviner pierre-feuille-ciseaux
        # prediction = model.predict(img)
        prediction = "pierre"  # exemple temporaire

        return {"result": prediction}
    except Exception as e:
        return {"error": str(e)}
