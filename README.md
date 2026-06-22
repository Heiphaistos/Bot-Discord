<div align="center">
  <h1>🤖 Bot Discord RSSDI</h1>
  <p><strong>Bot Discord Python complet pour diffuser les articles RSSDI et gérer une communauté avec économie, modération, jeux et tickets.</strong></p>

  ![Version](https://img.shields.io/badge/version-1.0.0-blue)
  ![Stack](https://img.shields.io/badge/stack-Python%203%20%2B%20discord.py%20%2B%20Docker-purple)
  ![Status](https://img.shields.io/badge/status-production-green)
  ![Repo](https://img.shields.io/badge/repo-Heiphaistos%2FBot--Discord--RSSDI-gray?logo=github)
</div>

---

## 📋 Description

Bot Discord self-hosted développé en Python pour la communauté RSSDI. Il automatise la publication des flux RSS dans des salons configurés et embarque un ensemble complet de fonctionnalités communautaires : économie, modération, jeux, tickets, logs avancés, giveaways et reaction-roles.

**Repo GitHub :** [Heiphaistos/Bot-Discord-RSSDI](https://github.com/Heiphaistos/Bot-Discord-RSSDI)

---

## ✨ Fonctionnalités

### 📡 RSS & RSSDI
- Abonnement aux flux RSS via l'API RSSDI
- Publication automatique dans des salons Discord configurés
- Détection des nouveaux articles et notification en temps réel

### 💰 Économie
- Solde, pièces quotidiennes, travail, crime, vol entre membres
- Classement, boutique, pari (pile ou face)

### 🛡️ Modération
- Kick, ban, unban, timeout, avertissements, auto-modération
- Commandes slash Discord (/) — interface moderne

### 🎮 Jeux
- Pierre-papier-ciseaux, devinette, trivia, boule 8, duel de réaction
- Chaîne de mots, plus-haut/plus-bas

### 🎫 Tickets de support
- Création, gestion, fermeture de tickets par canal dédié

### 📝 Logs avancés
- Messages supprimés/édités, bans, rôles, canaux — tout tracé

### 🎉 Extras
- Giveaways, reaction-roles, sondages, rappels, notes modération
- Outils : Base64, hash, Morse, QR code, UUID, timestamp Discord

---

## 🛠️ Stack technique

| Composant | Technologie |
|-----------|-------------|
| Langage | Python 3.10+ |
| Bot framework | discord.py (slash commands) |
| Base de données | SQLite (automatique au premier lancement) |
| Interface web | Flask (dashboard admin optionnel, port 5000) |
| Déploiement | Docker + docker-compose |

---

## 📁 Structure

```
Bot-Discord-RSSDI/
├── bot.py              # Point d'entrée principal
├── config.py           # Configuration centralisée
├── database.py         # Gestionnaire SQLite
├── cogs/               # Modules du bot
│   ├── economy.py      # Économie
│   ├── moderation.py   # Modération
│   ├── games.py        # Jeux
│   ├── tickets.py      # Tickets de support
│   ├── welcome.py      # Bienvenue / Au revoir
│   ├── logging.py      # Logs avancés
│   ├── polls.py        # Sondages
│   ├── reminders.py    # Rappels
│   ├── reactionroles.py
│   ├── giveaways.py
│   └── notes.py
├── utils/
│   ├── logger.py
│   └── security.py
├── templates/          # Interface web Flask
├── data/               # Base de données + logs
├── requirements_new.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🚀 Déploiement

### Prérequis

- Python 3.10+
- Docker + docker-compose (recommandé en prod)

### Installation locale

```bash
git clone https://github.com/Heiphaistos/Bot-Discord-RSSDI
cd Bot-Discord-RSSDI
pip install -r requirements_new.txt
cp .env.example .env
# Renseigner DISCORD_TOKEN
python bot.py
```

### Docker (production)

```bash
docker compose up -d
# Logs
docker compose logs -f bot
```

### Variables d'environnement (`.env`)

| Variable | Requis | Description |
|----------|--------|-------------|
| `DISCORD_TOKEN` | Oui | Token du bot Discord |
| `COMMAND_PREFIX` | Non | Préfixe commandes (défaut: `!`) |
| `DATABASE_URL` | Non | URL SQLite (défaut: local) |
| `ENABLE_RSS` | Non | Activer le module RSS (défaut: `true`) |
| `ENABLE_ECONOMY` | Non | Activer l'économie (défaut: `true`) |
| `DAILY_COINS` | Non | Pièces quotidiennes (défaut: `100`) |
| `MAX_WARNINGS` | Non | Avertissements avant ban (défaut: `5`) |
| `INTERFACE_PORT` | Non | Port dashboard web (défaut: `5000`) |

### Mise à jour

```bash
git pull
pip install -r requirements_new.txt --upgrade
# ou Docker :
docker compose pull && docker compose up -d --build
```

---

## 🔒 Sécurité

- Validation des entrées utilisateur sur toutes les commandes
- Rate limiting intégré (cooldown configurable)
- Calculateur mathématique sécurisé (sans `eval()`)
- Système de permissions Discord respecté
- Sessions Flask sécurisées pour l'interface web

---

## 📝 Licence

MIT — © 2026 Heiphaistos
