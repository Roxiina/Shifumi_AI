import pytest
from game_logic import get_result, finger_up, detect_sign

class MockLandmark:
    """Classe pour simuler les points de repère de la main"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

def create_mock_hand(finger_states):
    """
    Crée une main simulée avec les états des doigts spécifiés.
    
    Args:
        finger_states: Liste de booléens indiquant si chaque doigt est levé
                      [pouce, index, majeur, annulaire, auriculaire]
    """
    landmarks = []
    base_y = 0.5
    
    # Création de 21 points de repère (comme dans mediapipe)
    for i in range(21):
        if i in [4, 8, 12, 16, 20]:  # Points des bouts des doigts
            finger_index = [4, 8, 12, 16, 20].index(i)
            is_up = finger_states[finger_index]
            y = base_y - 0.2 if is_up else base_y + 0.2
            x = i * 0.05
            if i == 4:  # Pouce
                x = -0.1 if is_up else 0.3
        else:
            y = base_y
            x = i * 0.05
        landmarks.append(MockLandmark(x, y))
    
    return landmarks

def test_finger_up():
    """Test de la détection des doigts levés"""
    # Création d'une main simulée avec deux points
    # Premier test : doigt levé (y plus petit en haut)
    landmarks = [MockLandmark(0, 0.5), MockLandmark(0, 0.3)]
    assert finger_up(landmarks, 1, 0) == True, "Le doigt devrait être détecté comme levé"

    # Deuxième test : doigt baissé (y plus grand en haut)
    landmarks = [MockLandmark(0, 0.5), MockLandmark(0, 0.7)]
    assert finger_up(landmarks, 1, 0) == False, "Le doigt devrait être détecté comme baissé"

def test_detect_sign():
    """Test de la détection des signes"""
    # Test de la pierre (tous les doigts baissés)
    pierre_landmarks = create_mock_hand([False, False, False, False, False])
    assert detect_sign(pierre_landmarks) == "pierre", "Devrait détecter une pierre"

    # Test de la feuille (tous les doigts levés)
    feuille_landmarks = create_mock_hand([True, True, True, True, True])
    assert detect_sign(feuille_landmarks) == "feuille", "Devrait détecter une feuille"

    # Test des ciseaux (index et majeur levés)
    ciseaux_landmarks = create_mock_hand([False, True, True, False, False])
    assert detect_sign(ciseaux_landmarks) == "ciseaux", "Devrait détecter des ciseaux"

    # Test d'un geste inconnu (configuration aléatoire)
    inconnu_landmarks = create_mock_hand([True, False, True, False, True])
    assert detect_sign(inconnu_landmarks) == "inconnu", "Devrait détecter un geste inconnu"

def test_get_result():
    """Test de la détermination du gagnant"""
    # Test des égalités
    assert get_result("pierre", "pierre") == "Égalité"
    assert get_result("feuille", "feuille") == "Égalité"
    assert get_result("ciseaux", "ciseaux") == "Égalité"

    # Test des victoires du joueur
    assert get_result("pierre", "ciseaux") == "Joueur"
    assert get_result("feuille", "pierre") == "Joueur"
    assert get_result("ciseaux", "feuille") == "Joueur"

    # Test des victoires de l'ordinateur
    assert get_result("pierre", "feuille") == "Ordinateur"
    assert get_result("feuille", "ciseaux") == "Ordinateur"
    assert get_result("ciseaux", "pierre") == "Ordinateur"
