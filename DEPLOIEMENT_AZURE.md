# 🚀 Déploiement Shifumi AI sur Azure App Service

## ❌ IMPORTANT : Vous êtes sur Static Web Apps (incorrect)
Azure Static Web Apps ne supporte pas Flask/Python côté serveur.
Vous devez utiliser **Azure App Service** à la place.

## ✅ SOLUTION : Déployer sur Azure App Service

### Étape 1 : Supprimer le Static Web App actuel (optionnel)

```bash
# Supprimer la ressource Static Web App existante
az staticwebapp delete --name <nom-static-webapp> --resource-group <resource-group>
```

### Étape 2 : Créer un Azure App Service

```bash
# 1. Se connecter à Azure
az login

# 2. Créer un groupe de ressources
az group create --name shifumi-rg --location francecentral

# 3. Créer un App Service Plan Linux
az appservice plan create \
  --name shifumi-plan \
  --resource-group shifumi-rg \
  --sku B1 \
  --is-linux

# 4. Créer la Web App avec Python 3.11
az webapp create \
  --resource-group shifumi-rg \
  --plan shifumi-plan \
  --name shifumi-ai-<votre-nom> \
  --runtime "PYTHON:3.11"

# 5. Activer WebSockets (CRUCIAL pour SocketIO)
az webapp config set \
  --resource-group shifumi-rg \
  --name shifumi-ai-<votre-nom> \
  --web-sockets-enabled true

# 6. Configurer les paramètres
az webapp config appsettings set \
  --resource-group shifumi-rg \
  --name shifumi-ai-<votre-nom> \
  --settings \
    WEBSITES_PORT=8000 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true

# 7. Configurer le script de démarrage
az webapp config set \
  --resource-group shifumi-rg \
  --name shifumi-ai-<votre-nom> \
  --startup-file "startup.sh"

# 8. Déployer l'application
# Option A : Déploiement ZIP
Compress-Archive -Path app.py,game_logic.py,requirements.txt,startup.sh,templates,static -DestinationPath deploy.zip -Force
az webapp deploy \
  --resource-group shifumi-rg \
  --name shifumi-ai-<votre-nom> \
  --src-path deploy.zip \
  --type zip

# Option B : Déploiement Git
az webapp deployment source config-local-git \
  --name shifumi-ai-<votre-nom> \
  --resource-group shifumi-rg

git remote add azure <git-url-retournée>
git push azure main
```

### Étape 3 : Vérifier le déploiement

```bash
# Voir les logs en temps réel
az webapp log tail --name shifumi-ai-<votre-nom> --resource-group shifumi-rg

# Obtenir l'URL
az webapp show --name shifumi-ai-<votre-nom> --resource-group shifumi-rg --query defaultHostName -o tsv
```

## 📋 Checklist de déploiement

- [ ] Supprimer le Static Web App
- [ ] Créer un App Service Plan
- [ ] Créer la Web App avec Python
- [ ] Activer WebSockets
- [ ] Configurer le port 8000
- [ ] Ajouter startup.sh
- [ ] Déployer l'application
- [ ] Tester l'URL

## 💰 Coûts

- **Plan B1** : ~13€/mois (1.75GB RAM, 1 Core)
- **Plan F1** : Gratuit (limité, pas recommandé pour WebSocket)

## 🐛 Problèmes courants

### CSS ne charge pas
- Vérifier que `/static/style.css` existe
- Vider le cache : Ctrl+Shift+R
- Vérifier les logs d'erreur

### WebSocket ne fonctionne pas
```bash
# Vérifier que WebSocket est activé
az webapp config show --name shifumi-ai-<votre-nom> --resource-group shifumi-rg --query webSocketsEnabled
```

### MediaPipe/OpenCV erreurs
- Utiliser `opencv-python-headless` (déjà dans requirements.txt)
- Vérifier que les dépendances système sont installées (startup.sh)

## 🔗 URL finale

Votre application sera accessible à :
```
https://shifumi-ai-<votre-nom>.azurewebsites.net
```
