# -*- coding: utf-8 -*-
import cv2
import mediapipe as mp
import numpy as np
import random
import time
from game_logic import finger_up, detect_sign, get_result

# Configuration de MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Constantes pour le jeu
COUNTDOWN_TIME = 3  # Temps de compte à rebours en secondes
ROUND_PAUSE = 2    # Pause entre les manches en secondes
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

def draw_text_with_background(frame, text, position, scale=1, color=(255, 255, 255), thickness=2):
    """
    Dessine du texte avec un fond sombre pour une meilleure lisibilité
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), baseline = cv2.getTextSize(text, font, scale, thickness)
    
    # Dessiner le fond
    padding = 5
    cv2.rectangle(frame,
                 (position[0] - padding, position[1] - text_height - padding),
                 (position[0] + text_width + padding, position[1] + padding),
                 (0, 0, 0), -1)
    
    # Dessiner le texte
    cv2.putText(frame, text, position, font, scale, color, thickness)

def main():
    # Variables de gestion de la détection
    last_valid_choice = "inconnu"
    frames_without_detection = 0
    MAX_FRAMES_WITHOUT_DETECTION = 30  # Environ 1 seconde à 30 FPS
    reconnection_attempts = 0
    MAX_RECONNECTION_ATTEMPTS = 3
    cap = None

    while reconnection_attempts < MAX_RECONNECTION_ATTEMPTS:
        try:
            # Initialisation de la webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print(f"Tentative {reconnection_attempts + 1} de connexion à la webcam...")
                reconnection_attempts += 1
                time.sleep(1)
                continue

            # Configuration de la webcam
            available_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            available_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"Résolution disponible: {available_width}x{available_height}")

            target_width = min(WINDOW_WIDTH, available_width)
            target_height = min(WINDOW_HEIGHT, available_height)
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, target_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_height)
            
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"Résolution configurée: {actual_width}x{actual_height}")
            
            # Initialisation de MediaPipe
            print("Initialisation de MediaPipe Hands...")
            hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                model_complexity=0,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
            print("MediaPipe Hands initialisé avec succès!")

            # Variables du jeu
            score_joueur = 0
            score_ordi = 0
            last_play_time = 0
            computer_choice = "En attente..."
            game_state = "waiting"
            countdown_start = 0
            current_round_result = None
            player_choice = "inconnu"
            
            # Boucle principale du jeu
            while True:
                try:
                    ret, frame = cap.read()
                    if not ret:
                        print("Erreur de lecture de la caméra, tentative de récupération...")
                        time.sleep(0.1)
                        continue

                    frame = cv2.flip(frame, 1)
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    result = hands.process(rgb)

                    hand_detected = False
                    current_choice = "inconnu"

                    if result.multi_hand_landmarks:
                        hand_detected = True
                        frames_without_detection = 0
                        
                        for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                            hand_type = handedness.classification[0].label
                            landmarks = hand_landmarks.landmark
                            is_right_hand = (hand_type == "Right")
                            
                            # Dessiner les mains
                            mp_drawing.draw_landmarks(
                                frame, 
                                hand_landmarks, 
                                mp_hands.HAND_CONNECTIONS,
                                mp_drawing_styles.get_default_hand_landmarks_style(),
                                mp_drawing_styles.get_default_hand_connections_style()
                            )
                            
                            # Détecter le signe
                            current_choice = detect_sign(landmarks, is_right_hand)
                            if current_choice != "inconnu":
                                player_choice = current_choice
                                last_valid_choice = current_choice
                            
                            # Afficher les informations sur la main
                            hand_info = f"Main {'droite' if is_right_hand else 'gauche'} détectée"
                            draw_text_with_background(frame, hand_info, (10, 350), 1, (255, 255, 0), 2)
                    else:
                        frames_without_detection += 1
                        if frames_without_detection < MAX_FRAMES_WITHOUT_DETECTION and game_state != "waiting":
                            # Utiliser le dernier choix valide pendant un court moment
                            player_choice = last_valid_choice
                        else:
                            player_choice = "inconnu"

                    # Gestion des états du jeu
                    current_time = time.time()
                    
                    if game_state == "waiting":
                        computer_choice = "En attente..."
                        if player_choice != "inconnu":
                            game_state = "countdown"
                            countdown_start = current_time
                            current_round_result = None
                    
                    elif game_state == "countdown":
                        remaining_time = int(COUNTDOWN_TIME - (current_time - countdown_start))
                        if remaining_time <= 0:
                            if player_choice != "inconnu":
                                game_state = "playing"
                                computer_choice = random.choice(["pierre", "feuille", "ciseaux"])
                                current_round_result = get_result(player_choice, computer_choice)
                                
                                if current_round_result == "Joueur":
                                    score_joueur += 1
                                elif current_round_result == "Ordinateur":
                                    score_ordi += 1
                                
                                last_play_time = current_time
                            else:
                                game_state = "waiting"
                        else:
                            text = str(remaining_time)
                            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 4, 4)[0]
                            text_x = (actual_width - text_size[0]) // 2
                            text_y = (actual_height + text_size[1]) // 2
                            draw_text_with_background(frame, text, (text_x, text_y), 4, (255, 255, 255), 4)
                    
                    elif game_state == "playing":
                        if current_time - last_play_time > ROUND_PAUSE:
                            game_state = "waiting"

                    # Interface utilisateur
                    draw_text_with_background(frame, "SHIFUMI", (actual_width//2 - 100, 40), 2.0, (255, 215, 0), 3)

                    # Zone de jeu du joueur
                    draw_text_with_background(frame, "JOUEUR", (200, 100), 1.5, (0, 255, 0), 2)
                    draw_text_with_background(frame, f"Choix: {player_choice}", (200, 150), 1.1, (0, 255, 0), 2)
                    draw_text_with_background(frame, f"Score: {score_joueur}", (200, 200), 1.1, (0, 255, 0), 2)

                    # Zone de jeu de l'ordinateur
                    draw_text_with_background(frame, "ORDINATEUR", (actual_width - 400, 100), 1.5, (0, 255, 255), 2)
                    draw_text_with_background(frame, f"Choix: {computer_choice}", (actual_width - 400, 150), 1.1, (0, 255, 255), 2)
                    draw_text_with_background(frame, f"Score: {score_ordi}", (actual_width - 400, 200), 1.1, (0, 255, 255), 2)

                    # Afficher le résultat du round
                    if current_round_result:
                        result_color = (0, 255, 0) if current_round_result == "Joueur" else \
                                    (0, 255, 255) if current_round_result == "Ordinateur" else \
                                    (255, 255, 255)
                        text_size = cv2.getTextSize(current_round_result, cv2.FONT_HERSHEY_SIMPLEX, 2, 2)[0]
                        text_x = (actual_width - text_size[0]) // 2
                        draw_text_with_background(frame, current_round_result, (text_x, 300), 2, result_color, 2)

                    # Messages d'état et instructions
                    if not hand_detected:
                        draw_text_with_background(frame, "En attente de détection de main...", 
                            (actual_width//2 - 200, actual_height - 50), 1, (200, 200, 200), 2)
                    elif game_state == "waiting":
                        draw_text_with_background(frame, "Montrez votre main pour commencer", 
                            (actual_width//2 - 200, actual_height - 50), 1, (255, 255, 255), 2)

                    # Affichage de la fenêtre
                    cv2.imshow("Shifumi", frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q") or key == 27:  # q ou Échap pour quitter
                        break

                except Exception as e:
                    print(f"Erreur pendant le jeu: {e}")
                    time.sleep(0.1)
                    continue

            # Nettoyage
            if cap is not None:
                cap.release()
            cv2.destroyAllWindows()
            break

        except Exception as e:
            print(f"Erreur lors de l'initialisation: {e}")
            if cap is not None:
                cap.release()
            reconnection_attempts += 1
            if reconnection_attempts < MAX_RECONNECTION_ATTEMPTS:
                print("Nouvelle tentative dans 2 secondes...")
                time.sleep(2)
            else:
                print("Impossible d'initialiser le jeu après plusieurs tentatives.")
                return

if __name__ == "__main__":
    main()
