import cv2
import mediapipe as mp
import numpy as np
import random
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# --- Fonction de détection des signes ---
def finger_up(landmarks, tip, mcp):
    return landmarks[tip].y < landmarks[mcp].y

def detect_sign(landmarks):
    fingers = []

    # Index, middle, ring, pinky
    fingers.append(finger_up(landmarks, 8, 5))   # index
    fingers.append(finger_up(landmarks, 12, 9))  # middle
    fingers.append(finger_up(landmarks, 16, 13)) # ring
    fingers.append(finger_up(landmarks, 20, 17)) # pinky

    # Pouce (gauche ou droite)
    thumb = landmarks[4].x < landmarks[3].x
    fingers.insert(0, thumb)

    # Décision
    if fingers.count(True) == 0:
        return "pierre"
    elif fingers.count(True) == 5:
        return "feuille"
    elif fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
        return "ciseaux"
    else:
        return "inconnu"

# --- Fonction de résultat ---
def get_result(player, computer):
    if player == computer:
        return "Égalité"
    elif (player == "pierre" and computer == "ciseaux") or \
         (player == "feuille" and computer == "pierre") or \
         (player == "ciseaux" and computer == "feuille"):
        return "Joueur"
    else:
        return "Ordinateur"

# --- Programme principal ---
cap = cv2.VideoCapture(0)

with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8, min_tracking_confidence=0.8) as hands:
    score_joueur = 0
    score_ordi = 0
    last_play_time = 0
    computer_choice = "..."

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        player_choice = "inconnu"

        # Détection des mains
        if result.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                label = handedness.classification[0].label  # Left ou Right

                sign = detect_sign(hand_landmarks.landmark)

                if label == "Right":
                    player_choice = sign

        # Jeu toutes les 3 secondes
        current_time = time.time()
        if current_time - last_play_time > 3 and player_choice != "inconnu":
            computer_choice = random.choice(["pierre", "feuille", "ciseaux"])
            gagnant = get_result(player_choice, computer_choice)

            if gagnant == "Joueur":
                score_joueur += 1
            elif gagnant == "Ordinateur":
                score_ordi += 1

            last_play_time = current_time

        # --- Affichage ---
        cv2.putText(frame, f"Joueur: {player_choice}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0), 3)
        cv2.putText(frame, f"Ordinateur: {computer_choice}", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 3)
        cv2.putText(frame, f"Score Joueur: {score_joueur}", (10, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(frame, f"Score Ordi: {score_ordi}", (10, 210),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(frame, f"Press ESC pour quitter", (10, 470),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        cv2.imshow("🤖 Shifumi AI - Double joueur avec score", frame)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
