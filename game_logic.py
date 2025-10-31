def finger_up(landmarks, tip, mcp, ip=None):
    """
    Détermine si un doigt est levé en comparant les positions relatives.
    
    Args:
        landmarks: Liste des points de repère de la main
        tip: Index du bout du doigt
        mcp: Index de la base du doigt
        ip: Index de l'articulation intermédiaire (pour plus de précision)
    
    Returns:
        bool: True si le doigt est levé, False sinon
    """
    # Vérification plus précise avec l'articulation intermédiaire si disponible
    if ip is not None:
        return (landmarks[tip].y < landmarks[ip].y < landmarks[mcp].y)
    
    # Sinon, utilise la comparaison simple bout/base
    return landmarks[tip].y < landmarks[mcp].y

def detect_sign(landmarks, is_right_hand=True):
    """
    Détecte le signe (pierre, papier, ciseaux) à partir des points de repère de la main.
    
    Args:
        landmarks: Liste des points de repère de la main
        is_right_hand: True si c'est la main droite, False si c'est la main gauche
    
    Returns:
        str: "pierre", "papier", "ciseaux" ou "aucun"
    """
    # Vérification si les landmarks sont valides
    if not landmarks or len(landmarks) < 21:
        return "aucun"

    fingers = []
    
    # Vérification du pouce avec plus de précision en tenant compte de la main utilisée
    thumb_ip = landmarks[3]
    thumb_tip = landmarks[4]
    # Inverse la logique pour la main gauche
    thumb_up = thumb_tip.x < thumb_ip.x if is_right_hand else thumb_tip.x > thumb_ip.x
    fingers.append(thumb_up)

    # Vérification des autres doigts avec les articulations intermédiaires
    finger_landmarks = [
        (8, 7, 6),  # Index
        (12, 11, 10),  # Majeur
        (16, 15, 14),  # Annulaire
        (20, 19, 18)   # Auriculaire
    ]

    for tip, ip, mcp in finger_landmarks:
        is_up = finger_up(landmarks, tip, mcp, ip)
        fingers.append(is_up)

    # Détection améliorée des signes
    
    # Vérifier spécifiquement pour les ciseaux d'abord
    # Les ciseaux sont détectés si :
    # 1. L'index est levé
    # 2. Le majeur est levé
    # 3. L'annulaire est baissé OU le petit doigt est baissé
    if fingers[1] and fingers[2] and (not fingers[3] or not fingers[4]):
        return "ciseaux"
    
    # Compter le nombre total de doigts levés pour les autres signes
    num_fingers_up = fingers.count(True)
    
    # Pierre : poing fermé (0-1 doigts levés)
    if num_fingers_up <= 1:
        return "pierre"
    
    # Papier : la plupart des doigts levés (4-5 doigts)
    elif num_fingers_up >= 4:
        return "papier"
    
    # Si aucun signe n'est clairement identifié
    return "aucun"

def get_result(player, computer):
    """
    Détermine le gagnant d'une manche.
    
    Args:
        player: Choix du joueur ("pierre", "papier" ou "ciseaux")
        computer: Choix de l'ordinateur ("pierre", "papier" ou "ciseaux")
    
    Returns:
        str: "Égalité", "Joueur" ou "Ordinateur"
    """
    if player == computer:
        return "Égalité"
    elif (player == "pierre" and computer == "ciseaux") or \
         (player == "papier" and computer == "pierre") or \
         (player == "ciseaux" and computer == "papier"):
        return "Joueur"
    else:
        return "Ordinateur"