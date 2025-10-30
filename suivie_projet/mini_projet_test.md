# 🧩 TP : Tester le jeu Shifumi en Python

## 🎯 Objectif

Apprendre à **écrire et exécuter des tests automatisés** pour vérifier le bon fonctionnement du jeu **Shifumi (Pierre–Feuille–Ciseaux)** développé en Python.

---

## ⚙️ Compétences visées

* Comprendre le rôle des **tests unitaires**.
* Créer des tests avec **pytest**.
* Automatiser la vérification du code.
* Identifier et corriger les erreurs à l’aide des tests.

---

## 🧠 Contexte

Vous avez développé un jeu **Shifumi** en Python, où le joueur affronte l’ordinateur.
Votre mission est maintenant de **vérifier que toutes les règles du jeu sont respectées** à l’aide de tests automatisés.

---

## 🧩 Étapes du TP

### 1. 📦 Préparation de l’environnement

Dans votre dossier de projet **shifumi/**, créez un environnement virtuel et installez `pytest` :

```bash
python -m venv venv
source venv/bin/activate      # ou venv\Scripts\activate sous Windows
pip install pytest
```

Exemple de structure du projet :

```
shifumi/
│
├── game.py
└── tests/
    └── test_game.py
```

---

### 2. 🕹️ Code à tester

Voici un exemple de code du fichier `game.py` :

```python
import random

def get_computer_choice():
    return random.choice(["pierre", "feuille", "ciseaux"])

def determine_winner(player, computer):
    if player == computer:
        return "Égalité"
    elif (
        (player == "pierre" and computer == "ciseaux") or
        (player == "feuille" and computer == "pierre") or
        (player == "ciseaux" and computer == "feuille")
    ):
        return "Joueur"
    else:
        return "Ordinateur"
```

---

### 3. 🧪 Création des tests unitaires

Créez le fichier `tests/test_game.py` et ajoutez les tests suivants :

```python
from game import determine_winner

def test_egalite():
    assert determine_winner("pierre", "pierre") == "Égalité"
    assert determine_winner("feuille", "feuille") == "Égalité"
    assert determine_winner("ciseaux", "ciseaux") == "Égalité"

def test_victoires_joueur():
    assert determine_winner("pierre", "ciseaux") == "Joueur"
    assert determine_winner("feuille", "pierre") == "Joueur"
    assert determine_winner("ciseaux", "feuille") == "Joueur"

def test_victoires_ordinateur():
    assert determine_winner("pierre", "feuille") == "Ordinateur"
    assert determine_winner("feuille", "ciseaux") == "Ordinateur"
    assert determine_winner("ciseaux", "pierre") == "Ordinateur"
```

---

### 4. 🚀 Exécution des tests

Lancez tous les tests :

```bash
pytest
```

💡 Si tout est correct, les 9 tests doivent passer avec succès ✅

---

### 5. 🧩 Ajout de tests complémentaires

Ajouter des tests pour :

* Vérifier la gestion d’entrées invalides (par exemple : `"pierrex"`, `""`, etc.).
* Simuler plusieurs manches et calculer le score global.

---

### 6. 🤖 (Optionnel) Utilisation de l’IA pour générer des tests

Expérimentez un outil d’aide comme **CodiumAI** ou **GitHub Copilot** pour :

* Générer automatiquement de nouveaux cas de test.
* Vérifier si leurs tests couvrent tous les scénarios.

---

## 🧭 Questions de réflexion

1. À quoi servent les tests unitaires dans un projet Python ?
2. Pourquoi est-il important de tester tous les cas possibles ?
3. Quelle est la différence entre un test automatisé et une vérification manuelle ?
4. Comment l’IA peut-elle faciliter la création de tests ?

---

## 🏁 Bonus (pour aller plus loin)

* Ajouter une fonction qui joue plusieurs manches et afficher le gagnant final, puis tester ce comportement.
* Intégrer `pytest` dans une **pipeline CI/CD** (ex. : GitHub Actions).
* Utiliser la librairie **Hypothesis** pour générer automatiquement des entrées aléatoires.

---
