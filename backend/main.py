from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import io, base64, random
from backend.model_client import ShifumiModel  # import correct

app = FastAPI()

# CORS pour autoriser le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance du modèle
model = ShifumiModel()

# Classe pour le POST JSON
class PredictRequest(BaseModel):
    image_base64: str

@app.post("/predict")
async def predict(req: PredictRequest):
    try:
        b64 = req.image_base64
        if b64.startswith("data:"):
            b64 = b64.split(",", 1)[1]
        img_bytes = io.BytesIO(base64.b64decode(b64))
        img = Image.open(img_bytes).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur décodage image: {e}")

    user_gesture, score = model.predict_image(img)
    choices = ["pierre", "feuille", "ciseaux"]
    server_choice = random.choice(choices)
    result = compute_result(user_gesture, server_choice)

    return {
        "user": user_gesture,
        "score": float(score),
        "server": server_choice,
        "result": result
    }

def compute_result(user, server):
    if user == server:
        return "egalite"
    wins = {"pierre":"ciseaux","ciseaux":"feuille","feuille":"pierre"}
    return "gagne" if wins.get(user) == server else "perdu"

# Endpoint test minimal
@app.get("/")
def read_root():
    return {"message": "Shifumi AI fonctionne !"}
