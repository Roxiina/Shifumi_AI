# 🎮 Shifumi AI - Jeu de Pierre-Feuille-Ciseaux avec Intelligence Artificielle

Ce projet est une implémentation interactive du jeu Pierre-Feuille-Ciseaux utilisant la reconnaissance de gestes par intelligence artificielle via votre webcam.

## 📋 Prérequis

- Python 3.8 ou version ultérieure
- Une webcam fonctionnelle
- Windows, macOS, ou Linux

## 🚀 Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/Roxiina/Shifumi_AI.git
cd Shifumi_AI
```

2. Créez un environnement virtuel :
```bash
python -m venv .venv
```

3. Activez l'environnement virtuel :
   - Windows :
   ```bash
   .venv\Scripts\activate
   ```
   - macOS/Linux :
   ```bash
   source .venv/bin/activate
   ```

4. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## 🎯 Comment jouer

1. Lancez le jeu :
```bash
python shifumi_webcam.py
```

2. Positionnez votre main devant la webcam dans la zone de détection.

3. Faites les gestes suivants :
   - ✊ **Pierre** : Fermez le poing
   - ✋ **Feuille** : Ouvrez la main avec tous les doigts tendus
   - ✌️ **Ciseaux** : Levez uniquement l'index et le majeur

4. Le premier à atteindre 5 points gagne la partie !

## 🎮 Commandes du jeu

- `ESC` : Quitter le jeu
- `R` : Réinitialiser les scores
- Espace : Commencer une nouvelle partie

## 🔍 Structure du projet

```
Shifumi_AI/
├── shifumi_webcam.py     # Programme principal
├── game_logic.py         # Logique du jeu
├── models/
│   └── best.pt          # Modèle YOLOv5 entraîné
├── test/
│   └── test_game.py     # Tests unitaires
└── requirements.txt      # Dépendances Python
```

## 🧪 Tests

Pour exécuter les tests unitaires :
```bash
pytest test/test_game.py -v
```

## 🛠️ Technologies utilisées

- OpenCV : Capture et traitement vidéo
- MediaPipe : Détection des mains
- NumPy : Calculs mathématiques
- PyTest : Tests unitaires

## 📝 License

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commit vos changements
4. Push sur la branche
5. Ouvrir une Pull Request
