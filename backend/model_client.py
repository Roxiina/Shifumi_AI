from ultralytics import YOLO
from PIL import Image

class ShifumiModel:
    def __init__(self):
        # Charge ton modèle YOLO
        self.model = YOLO("backend/models/best.pt")

    def predict(self, image: Image.Image):
        # Prédit le geste sur une image PIL
        results = self.model.predict(image)
        if results and len(results[0].boxes) > 0:
            cls_id = int(results[0].boxes.cls[0])
            classes_map = {0: "pierre", 1: "papier", 2: "ciseaux"}
            return classes_map.get(cls_id, "inconnu")
        return "inconnu"
