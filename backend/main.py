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
image_base64: str # data URI ou base64 sans header


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