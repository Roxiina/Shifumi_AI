from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import cv2
import mediapipe as mp
import numpy as np
import base64
import json
from datetime import datetime
import os
from game_logic import detect_sign, get_result
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shifumi_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Variables globales pour le jeu
game_state = {
    'player_score': 0,
    'computer_score': 0,
    'current_round': 0,
    'points_to_win': 5,    # Points nécessaires pour gagner la partie
    'game_over': False,
    'last_result': None,
    'game_history': [],    # Historique des rounds
    'countdown_active': False,  # Indique si un compte à rebours est en cours
    'round_in_progress': False,  # Indique si un round est en cours
    'last_round_time': 0,  # Timestamp du dernier round
    'detected_hand': 'aucun'  # Main détectée par la caméra
}

def load_scores():
    """Charge l'historique des scores"""
    if os.path.exists("web_scores.json"):
        try:
            with open("web_scores.json", 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_score(winner, player_score, computer_score, game_history):
    """Sauvegarde le résultat d'une partie"""
    scores = load_scores()
    score_entry = {
        'date': datetime.now().isoformat(),
        'winner': winner,
        'player_score': player_score,
        'computer_score': computer_score,
        'game_details': game_history,
        'total_rounds': len(game_history)
    }
    scores.append(score_entry)
    
    # Garder seulement les 100 dernières parties
    if len(scores) > 100:
        scores = scores[-100:]
    
    with open("web_scores.json", 'w') as f:
        json.dump(scores, f, indent=2)

def reset_game():
    """Remet à zéro l'état du jeu"""
    global game_state
    game_state.update({
        'player_score': 0,
        'computer_score': 0,
        'current_round': 0,
        'game_over': False,
        'last_result': None,
        'game_history': [],
        'countdown_active': False,
        'round_in_progress': False,
        'detected_hand': 'aucun'
    })

def reset_match():
    """Remet à zéro une manche"""
    global game_state
    
    # Sauvegarder les résultats de la manche actuelle
    if game_state['current_round'] > 0:
        match_result = {
            'match_number': game_state['current_match'],
            'player_score': game_state['player_score'],
            'computer_score': game_state['computer_score'],
            'rounds_played': game_state['current_round'],
            'winner': 'Joueur' if game_state['player_score'] > game_state['computer_score'] else 'Ordinateur'
        }
        game_state['match_history'].append(match_result)
        
        # Incrémenter le compteur de manches gagnées
        if game_state['player_score'] > game_state['computer_score']:
            game_state['player_matches_won'] += 1
        else:
            game_state['computer_matches_won'] += 1
    
    # Reset des scores de la manche
    game_state.update({
        'player_score': 0,
        'computer_score': 0,
        'current_round': 0,
        'match_over': False,
        'last_result': None,
        'countdown_active': False,
        'round_in_progress': False,
        'last_round_time': 0
    })
    
    # Passer à la manche suivante
    game_state['current_match'] += 1
    
    # Vérifier si la partie est terminée (2 manches gagnées sur 3)
    if (game_state['player_matches_won'] >= 2 or 
        game_state['computer_matches_won'] >= 2 or 
        game_state['current_match'] > game_state['total_matches']):
        
        game_state['game_over'] = True
        
        # Déterminer le gagnant final
        if game_state['player_matches_won'] > game_state['computer_matches_won']:
            winner = 'Joueur'
        else:
            winner = 'Ordinateur'
        
        # Sauvegarder les résultats de la partie
        save_score(winner, game_state['player_matches_won'], 
                  game_state['computer_matches_won'], game_state['match_history'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scores')
def scores():
    scores_data = load_scores()
    
    # Calculer les statistiques
    total_games = len(scores_data)
    player_wins = sum(1 for score in scores_data if score['winner'] == 'Joueur')
    computer_wins = total_games - player_wins
    
    stats = {
        'total_games': total_games,
        'player_wins': player_wins,
        'computer_wins': computer_wins,
        'win_rate': round((player_wins / total_games * 100) if total_games > 0 else 0, 1)
    }
    
    # Inverser l'ordre pour afficher les plus récents en premier
    scores_data.reverse()
    
    return render_template('scores.html', scores=scores_data, stats=stats)

@app.route('/api/game/state')
def get_game_state():
    """Retourne l'état actuel du jeu"""
    return jsonify(game_state)

@app.route('/api/game/reset', methods=['POST'])
def api_reset_game():
    """Reset complet du jeu"""
    reset_game()
    return jsonify({'status': 'success', 'message': 'Jeu remis à zéro'})

@app.route('/api/game/play', methods=['POST'])
def api_play():
    """Joue un round avec le geste fourni"""
    data = request.get_json()
    player_gesture = data.get('gesture')
    
    # Vérifier le délai de 5 secondes
    current_time = datetime.now().timestamp()
    if (game_state['last_round_time'] > 0 and 
        current_time - game_state['last_round_time'] < 5):
        time_remaining = 5 - (current_time - game_state['last_round_time'])
        return jsonify({
            'status': 'wait',
            'message': f'Attendez encore {time_remaining:.1f} secondes',
            'time_remaining': time_remaining
        })
    
    if game_state['game_over'] or not player_gesture or player_gesture == 'aucun':
        return jsonify({'status': 'error', 'message': 'Geste invalide ou jeu terminé'})
    
    # Générer le geste de l'ordinateur
    computer_gesture = random.choice(['pierre', 'papier', 'ciseaux'])
    
    # Déterminer le résultat
    result = get_result(player_gesture, computer_gesture)
    
    # Mettre à jour les scores
    if result == "Gagné":
        game_state['player_score'] += 1
    elif result == "Perdu":
        game_state['computer_score'] += 1
    
    game_state['current_round'] += 1
    game_state['last_round_time'] = current_time
    game_state['last_result'] = {
        'player_gesture': player_gesture,
        'computer_gesture': computer_gesture,
        'result': result,
        'round': game_state['current_round']
    }
    
    # Vérifier si la manche est terminée (premier à 5 points)
    if (game_state['player_score'] >= game_state['rounds_per_game'] or 
        game_state['computer_score'] >= game_state['rounds_per_game']):
        game_state['match_over'] = True
        
        # Préparer automatiquement la manche suivante
        reset_match()
    
    return jsonify({
        'status': 'success',
        'result': result,
        'player_gesture': player_gesture,
        'computer_gesture': computer_gesture,
        'game_state': game_state
    })

@socketio.on('connect')
def handle_connect():
    print('Client connecté')
    emit('game_state', game_state)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client déconnecté')

@socketio.on('detect_gesture')
def handle_gesture_detection(data):
    """Traite l'image reçue pour détecter les gestes"""
    try:
        # Décoder l'image base64
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Traiter avec MediaPipe
        with mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        ) as hands:
            
            # Convertir BGR vers RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            detected_gesture = "aucun"
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Détecter le geste
                    detected_gesture = detect_sign(hand_landmarks.landmark)
            
            # Retourner le résultat
            emit('gesture_detected', {'gesture': detected_gesture})
            
    except Exception as e:
        print(f"Erreur lors du traitement de l'image: {e}")
        emit('gesture_detected', {'gesture': 'erreur'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)