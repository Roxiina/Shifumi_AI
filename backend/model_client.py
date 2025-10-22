from ultralytics import YOLO
from PIL import Image

class ShifumiModel:
    def __init__(self):
        # Chemin vers ton modèle local
        self.model = YOLO("backend/models/best.pt")

    def predict_image(self, pil_image: Image.Image):
        results = self.model(pil_image)
        if results and len(results) > 0:
            best = results[0]
            if best.boxes is not None and len(best.boxes) > 0:
                cls_id = int(best.boxes.cls[0])
                label = best.names[cls_id]  # pierre / feuille / ciseaux
                score = float(best.boxes.conf[0])
                return label, score
        return "inconnu", 0.0
