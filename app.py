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

def determine_winner(player_gesture, computer_gesture):
    """Détermine le gagnant d'un round"""
    if player_gesture == computer_gesture:
        return 'draw'
    elif ((player_gesture == 'pierre' and computer_gesture == 'ciseaux') or
          (player_gesture == 'papier' and computer_gesture == 'pierre') or
          (player_gesture == 'ciseaux' and computer_gesture == 'papier')):
        return 'player'
    else:
        return 'computer'

def emit_game_update(event_type):
    """Émet une mise à jour de l'état du jeu"""
    socketio.emit('game_state', {
        'state': game_state,
        'event': event_type
    })

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
    win_rate = round((player_wins / total_games * 100) if total_games > 0 else 0, 1)
    
    stats = {
        'total_games': total_games,
        'player_wins': player_wins,
        'computer_wins': computer_wins,
        'win_rate': win_rate
    }
    
    # Trier par date (plus récent en premier)
    scores_data.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('scores.html', scores=scores_data, stats=stats)

@app.route('/api/game/state')
def get_game_state():
    return jsonify(game_state)

@app.route('/api/game/reset', methods=['POST'])
def reset_game_api():
    reset_game()
    return jsonify({'status': 'success', 'game_state': game_state})

@app.route('/reset', methods=['POST'])
def reset_game_route():
    reset_game()
    return jsonify(game_state)

@app.route('/play', methods=['POST'])
def play():
    global game_state
    player_gesture = request.json.get('gesture')
    
    if not player_gesture or player_gesture not in ['pierre', 'papier', 'ciseaux']:
        return jsonify({'error': 'Geste invalide'}), 400
    
    if game_state['game_over']:
        return jsonify({'error': 'Partie terminée'}), 400
    
    computer_gesture = random.choice(['pierre', 'papier', 'ciseaux'])
    result = determine_winner(player_gesture, computer_gesture)
    
    game_state['current_round'] += 1
    
    # Enregistrer le round dans l'historique
    round_data = {
        'round': game_state['current_round'],
        'player_gesture': player_gesture,
        'computer_gesture': computer_gesture,
        'result': result,
        'timestamp': datetime.now().isoformat()
    }
    game_state['game_history'].append(round_data)
    
    # Mettre à jour les scores
    if result == 'player':
        game_state['player_score'] += 1
    elif result == 'computer':
        game_state['computer_score'] += 1
    
    game_state['last_result'] = result
    
    # Vérifier si quelqu'un a atteint 5 points
    if game_state['player_score'] >= game_state['points_to_win']:
        game_state['game_over'] = True
        winner = 'Joueur'
        save_score(winner, game_state['player_score'], game_state['computer_score'], game_state['game_history'])
        emit_game_update('game_over')
    elif game_state['computer_score'] >= game_state['points_to_win']:
        game_state['game_over'] = True
        winner = 'IA'
        save_score(winner, game_state['player_score'], game_state['computer_score'], game_state['game_history'])
        emit_game_update('game_over')
    else:
        emit_game_update('round_over')
    
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
    global game_state
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
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:
            
            detected_gesture = 'aucun'
            
            # Convertir BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Détecter le geste
                    detected_gesture = detect_sign(hand_landmarks.landmark)
            
            # Mettre à jour l'état avec la main détectée
            game_state['detected_hand'] = detected_gesture
            
            # Retourner le résultat
            emit('gesture_detected', {
                'gesture': detected_gesture,
                'hand_detected': detected_gesture != 'aucun'
            })
            
    except Exception as e:
        print(f"Erreur lors du traitement de l'image: {e}")
        emit('gesture_detected', {'gesture': 'aucun', 'hand_detected': False})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)