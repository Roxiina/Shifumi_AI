# 🗑️ Éléments Superflus du Projet Shifumi AI

Ce document liste tous les éléments qui ne sont pas nécessaires au fonctionnement du projet et qui peuvent être supprimés en toute sécurité.

## 📁 Dossiers à Supprimer

### 1. Dossier `yolov5/`
- Description : Framework de détection d'objets non utilisé
- Raison : Notre projet utilise MediaPipe pour la détection des mains
- Contenu superflu :
  - Tous les fichiers de configuration YOLOv5
  - Scripts d'entraînement et de détection
  - Fichiers de documentation YOLOv5

### 2. Dossier `models/`
- Description : Contient des modèles pré-entraînés non utilisés
- Raison : MediaPipe intègre déjà son propre modèle de détection
- Fichiers superflus :
  - `best.pt` (modèle YOLOv5)
  - Autres fichiers de modèles

### 3. Dossiers de cache
- `__pycache__/` : Cache Python (se régénère automatiquement)
- `.pytest_cache/` : Cache des tests (se régénère automatiquement)

## 📄 Fichiers à Supprimer

### 1. Fichiers de sauvegarde
- `shifumi_webcam.py.bak` : Copie de sauvegarde du fichier principal
- Raison : Version redondante du code source

### 2. Fichiers temporaires
- `mini_projet_test.md` : Version test du document projet
- `uv.lock` : Fichier de verrouillage temporaire
- Raison : Fichiers de travail non nécessaires en production

### 3. Fichiers de configuration inutilisés
- Configurations YOLOv5 diverses
- Fichiers de paramètres non utilisés

## 🔄 Comment Nettoyer le Projet

### Commande PowerShell pour supprimer les éléments superflus :
```powershell
Remove-Item -Path "yolov5","mini_projet_test.md","shifumi_webcam.py.bak","uv.lock","models","__pycache__",".pytest_cache" -Recurse -Force
```

## ✅ Fichiers Essentiels à Conserver

Pour référence, voici les fichiers qui sont nécessaires au fonctionnement du projet :

1. **Fichiers Sources**
   - `shifumi_webcam.py` : Programme principal
   - `game_logic.py` : Logique du jeu

2. **Tests**
   - `test/test_game.py` : Tests unitaires

3. **Configuration**
   - `requirements.txt` : Dépendances Python

4. **Documentation**
   - `README.md` : Guide d'installation et d'utilisation
   - `FEEDBACK.md` : Retour d'expérience
   - `mini_projet.md` : Documentation du projet

5. **Données**
   - `scores.json` : Historique des scores (généré automatiquement)

## 📝 Notes

- Les fichiers cache Python (`*.pyc`, `__pycache__`) seront automatiquement régénérés si nécessaire
- La suppression de ces éléments superflus réduira significativement la taille du projet
- Aucun impact sur les fonctionnalités du jeu
- Améliore la maintenabilité du code