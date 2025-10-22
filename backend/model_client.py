# backend/model_client.py
# Wrapper simple pour appeler l'API d'inference Hugging Face


import os
import io
import requests
from PIL import Image


HF_API_URL = os.getenv('HF_API_URL') # ex: https://api-inference.huggingface.co/models/username/modelname
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