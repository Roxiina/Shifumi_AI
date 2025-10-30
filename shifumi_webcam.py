# -*- coding: utf-8 -*-
import cv2
import mediapipe as mp
import numpy as np
import random
import time
from game_logic import finger_up, detect_sign, get_result
from datetime import datetime
import os
import json

# Configuration de MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Constantes pour le jeu
COUNTDOWN_TIME = 3  # Temps de compte à rebours en secondes
ROUND_PAUSE = 2    # Pause entre les manches en secondes
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
SCORE_MAX = 5      # Score maximum pour gagner
SCORES_FILE = "scores.json"

def load_scores():
    """Charge l'historique des scores"""
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_score(scores, winner, score_joueur, score_ordi):
    """Sauvegarde le résultat de la partie"""
    game_result = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "winner": winner,
        "score_joueur": score_joueur,
        "score_ordi": score_ordi
    }
    scores.append(game_result)
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f, indent=2)

def show_final_scores(scores):
    """Affiche le tableau des scores"""
    height = 720
    width = 1280
    background = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Titre
    cv2.putText(background, "TABLEAU DES SCORES", (width//2 - 200, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
    
    # En-têtes
    headers = ["Date", "Gagnant", "Score Joueur", "Score Ordinateur"]
    x_positions = [50, 350, 600, 850]
    for header, x in zip(headers, x_positions):
        cv2.putText(background, header, (x, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Afficher les 10 derniers scores
    start_y = 150
    recent_scores = scores[-10:] if len(scores) > 10 else scores
    for i, score in enumerate(recent_scores):
        y = start_y + i * 40
        cv2.putText(background, score["date"], (50, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        cv2.putText(background, score["winner"], (350, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        cv2.putText(background, str(score["score_joueur"]), (600, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        cv2.putText(background, str(score["score_ordi"]), (850, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    
    # Instructions
    cv2.putText(background, "Appuyez sur une touche pour quitter", (width//2 - 200, height - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
    
    # Afficher le tableau
    cv2.imshow("Tableau des Scores", background)
    cv2.waitKey(0)
    cv2.destroyWindow("Tableau des Scores")

def draw_text_with_background(frame, text, position, scale=1, color=(255, 255, 255), thickness=2):
    """Dessine du texte avec un fond simple pour une meilleure lisibilité"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), baseline = cv2.getTextSize(text, font, scale, thickness)
    
    # Calcul des dimensions du rectangle
    padding = 5
    x1 = position[0] - padding
    y1 = position[1] - text_height - padding
    x2 = position[0] + text_width + padding
    y2 = position[1] + padding

    # Dessiner le fond noir
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), -1)
    
    # Dessiner le texte
    cv2.putText(frame, text, position, font, scale, color, thickness)
    
    # Dessiner le texte avec contour pour plus de lisibilité
    # Contour noir
    cv2.putText(frame, text, position, font, scale, (0, 0, 0), thickness + 2)
    # Texte principal
    cv2.putText(frame, text, position, font, scale, color, thickness)

def show_game_over(frame, winner, score_joueur, score_ordi):
    """Affiche l'écran de fin de partie"""
    height, width = frame.shape[:2]
    
    # Fond noir semi-transparent
    overlay = np.zeros_like(frame)
    cv2.addWeighted(frame, 0.3, overlay, 0.7, 0, frame)
    
    # Position centrale pour le texte
    center_y = height // 2
    
    # Message de victoire
    if winner == "Joueur":
        message = "VICTOIRE DU JOUEUR !"
        winner_color = (0, 255, 0)
    else:
        message = "VICTOIRE DE L'ORDINATEUR !"
        winner_color = (0, 255, 255)
    
    # Centrer le texte
    text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 3)[0]
    text_x = (width - text_size[0]) // 2
    draw_text_with_background(frame, message, 
                            (text_x, center_y - 60), 
                            2.0, winner_color, 3)
    
    # Score final
    score_text = f"Score Final - Joueur : {score_joueur}  Ordinateur : {score_ordi}"
    text_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
    text_x = (width - text_size[0]) // 2
    draw_text_with_background(frame, score_text, 
                            (text_x, center_y), 
                            1.0, (255, 255, 255), 2)
    
    # Instructions
    instructions = [
        ["[R] Recommencer", (255, 255, 255)],
        ["[ESPACE] Voir les scores", (255, 255, 255)],
        ["[Q] Quitter", (255, 255, 255)]
    ]
    
    for i, (text, color) in enumerate(instructions):
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
        text_x = (width - text_size[0]) // 2
        draw_text_with_background(frame, text, 
                                (text_x, center_y + 40 + i * 40), 
                                1.0, color, 2)
    
    cv2.imshow("Shifumi", frame)
    
    cv2.imshow("Shifumi", frame)

def main():
    # Variables de gestion de la détection
    last_valid_choice = "inconnu"
    frames_without_detection = 0
    MAX_FRAMES_WITHOUT_DETECTION = 30  # Environ 1 seconde à 30 FPS
    reconnection_attempts = 0
    MAX_RECONNECTION_ATTEMPTS = 3
    cap = None

    # Charger l'historique des scores
    scores = load_scores()

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
            game_over = False
            
            # Boucle principale du jeu
            while True:
                try:
                    ret, frame = cap.read()
                    if not ret:
                        print("Erreur de lecture de la caméra, tentative de récupération...")
                        time.sleep(0.1)
                        continue

                    frame = cv2.flip(frame, 1)

                    # Si le jeu est terminé, afficher l'écran de fin
                    if game_over:
                        winner = "Joueur" if score_joueur > score_ordi else "Ordinateur"
                        show_game_over(frame, winner, score_joueur, score_ordi)
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord(" "):  # Espace pour voir les scores
                            show_final_scores(scores)
                        elif key == ord("r"):  # R pour recommencer
                            # Réinitialiser les variables du jeu
                            score_joueur = 0
                            score_ordi = 0
                            game_state = "waiting"
                            computer_choice = "En attente..."
                            current_round_result = None
                            player_choice = "inconnu"
                            game_over = False
                        elif key == ord("q"):  # Q pour quitter
                            break
                        continue

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
                            hand_info = "Main DROITE detectee" if is_right_hand else "Main GAUCHE detectee"
                            text_size = cv2.getTextSize(hand_info, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
                            text_x = actual_width - text_size[0] - 20
                            draw_text_with_background(frame, hand_info, (text_x, 350), 1, (255, 255, 0), 2)
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
                                
                                # Vérifier si le score maximum est atteint
                                if score_joueur >= SCORE_MAX or score_ordi >= SCORE_MAX:
                                    winner = "Joueur" if score_joueur > score_ordi else "Ordinateur"
                                    save_score(scores, winner, score_joueur, score_ordi)
                                    game_over = True
                                
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

                    # Interface utilisateur - Titre
                    title = "SHIFUMI"
                    text_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 3)[0]
                    text_x = (actual_width - text_size[0]) // 2
                    draw_text_with_background(frame, title, (text_x, 50), 2.0, (255, 215, 0), 3)

                    # Zone de jeu du joueur
                    draw_text_with_background(frame, "JOUEUR", (50, 100), 1.5, (0, 255, 0), 2)
                    draw_text_with_background(frame, f"Choix : {player_choice.upper()}", (50, 150), 1.0, (0, 255, 0), 2)
                    draw_text_with_background(frame, f"Score : {score_joueur}/{SCORE_MAX}", (50, 200), 1.0, (0, 255, 0), 2)

                    # Zone de jeu de l'ordinateur
                    draw_text_with_background(frame, "ORDINATEUR", (actual_width - 300, 100), 1.5, (0, 255, 255), 2)
                    draw_text_with_background(frame, f"Choix : {computer_choice}", (actual_width - 300, 150), 1.0, (0, 255, 255), 2)
                    draw_text_with_background(frame, f"Score : {score_ordi}/{SCORE_MAX}", (actual_width - 300, 200), 1.0, (0, 255, 255), 2)

                    # Afficher le résultat du round
                    if current_round_result:
                        if current_round_result == "Joueur":
                            result_text = "VICTOIRE DU JOUEUR"
                            result_color = (0, 255, 0)
                        elif current_round_result == "Ordinateur":
                            result_text = "VICTOIRE DE L'ORDINATEUR"
                            result_color = (0, 255, 255)
                        else:
                            result_text = "EGALITE"
                            result_color = (255, 255, 255)
                        
                        text_size = cv2.getTextSize(result_text, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 2)[0]
                        text_x = (actual_width - text_size[0]) // 2
                        draw_text_with_background(frame, result_text, 
                                               (text_x, actual_height//2), 2, result_color, 2)

                    # Messages d'état et instructions
                    if not hand_detected:
                        message = "En attente de detection de main..."
                        text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
                        text_x = (actual_width - text_size[0]) // 2
                        draw_text_with_background(frame, message, 
                            (text_x, actual_height - 50), 1, (200, 200, 200), 2)
                    elif game_state == "waiting":
                        message = "Montrez votre main pour commencer"
                        text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
                        text_x = (actual_width - text_size[0]) // 2
                        draw_text_with_background(frame, message, 
                            (text_x, actual_height - 50), 1, (255, 255, 255), 2)

                    if not game_over:
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