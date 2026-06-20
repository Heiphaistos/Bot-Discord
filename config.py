"""
Configuration centralisée du bot Discord
"""
import os
from pathlib import Path
from typing import Dict, Any
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Avertissement: python-dotenv non installé. Les variables d'environnement du fichier .env ne seront pas chargées.")


def _require_env(key: str) -> str:
    """Retourne la valeur d'une variable d'environnement obligatoire ou lève une erreur."""
    val = os.environ.get(key)
    if not val:
        raise RuntimeError(f"La variable d'environnement obligatoire '{key}' n'est pas définie")
    return val


class Config:
    """Configuration principale du bot"""
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Discord
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")
    
    # Base de données
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/bot.db")
    
    # Interface web
    INTERFACE_SECRET = _require_env("INTERFACE_SECRET")
    INTERFACE_PASSWORD = _require_env("INTERFACE_PASSWORD")
    INTERFACE_HOST = os.getenv("INTERFACE_HOST", "127.0.0.1")
    INTERFACE_PORT = int(os.getenv("INTERFACE_PORT", "5000"))
    
    # Webhooks
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
    LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
    
    # Fonctionnalités
    ENABLE_RSS = os.getenv("ENABLE_RSS", "true").lower() == "true"
    ENABLE_ECONOMY = os.getenv("ENABLE_ECONOMY", "true").lower() == "true"
    ENABLE_GAMES = os.getenv("ENABLE_GAMES", "true").lower() == "true"
    ENABLE_AUTOMOD = os.getenv("ENABLE_AUTOMOD", "true").lower() == "true"
    
    # Limites
    MAX_WARNINGS = int(os.getenv("MAX_WARNINGS", "5"))
    MAX_XP_PER_MESSAGE = int(os.getenv("MAX_XP_PER_MESSAGE", "5"))
    COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "60"))
    
    # Economie
    DAILY_COINS = int(os.getenv("DAILY_COINS", "100"))
    WORK_COINS_MIN = int(os.getenv("WORK_COINS_MIN", "10"))
    WORK_COINS_MAX = int(os.getenv("WORK_COINS_MAX", "50"))
    
    @classmethod
    def validate(cls) -> bool:
        """Valide la configuration"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN manquant dans les variables d'environnement")
        
        # Créer les dossiers nécessaires
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        
        return True
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Retourne la config sous forme de dictionnaire"""
        return {
            key: getattr(cls, key) 
            for key in dir(cls) 
            if not key.startswith('_') and not callable(getattr(cls, key))
        }

# Validation au chargement
Config.validate()