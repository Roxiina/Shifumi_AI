import requests
import json

# Test de l'endpoint /play
def test_play_endpoint():
    url = "http://127.0.0.1:5000/play"
    data = {"gesture": "pierre"}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erreur: {e}")
        return False

# Test de l'endpoint /api/game/state
def test_game_state():
    url = "http://127.0.0.1:5000/api/game/state"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Game State: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    print("=== Test de l'état du jeu ===")
    test_game_state()
    
    print("\n=== Test du jeu (pierre) ===")
    test_play_endpoint()
    
    print("\n=== Test de l'état après jeu ===")
    test_game_state()