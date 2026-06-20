"""
Interface web moderne et sécurisée pour le bot Discord
"""
import os
from flask import render_template
import json
import asyncio
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from functools import wraps

from flask import Flask, request, render_template_string, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import aiosqlite
import time
import threading

from config import Config
from database import db_manager
from utils.security import session_manager, input_validator
from utils.logger import setup_logging

logger = setup_logging()

app = Flask(__name__)
app.secret_key = Config.INTERFACE_SECRET
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 heure

# ── Rate limiting login ────────────────────────────────────────────────────────
_login_attempts: dict = {}   # ip -> [timestamps]
_login_lock = threading.Lock()
_LOGIN_MAX = 5        # tentatives max
_LOGIN_WINDOW = 300   # fenêtre en secondes (5 minutes)


def _login_is_rate_limited(ip: str) -> bool:
    """Retourne True si l'IP a dépassé la limite de tentatives de connexion."""
    now = time.time()
    with _login_lock:
        attempts = [t for t in _login_attempts.get(ip, []) if now - t < _LOGIN_WINDOW]
        _login_attempts[ip] = attempts
        if len(attempts) >= _LOGIN_MAX:
            return True
        attempts.append(now)
        _login_attempts[ip] = attempts
    return False

# Heure de démarrage de l'interface (pour l'uptime)
START_TIME = datetime.now()

# Hash du mot de passe admin (à faire une seule fois)
ADMIN_PASSWORD_HASH = generate_password_hash(Config.INTERFACE_PASSWORD)

# Templates HTML modernes
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Bot Discord{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {
            --discord-blurple: #5865F2;
            --discord-dark: #2C2F33;
            --discord-darker: #23272A;
        }
        
        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .navbar {
            background: linear-gradient(135deg, var(--discord-blurple), #4752C4);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.2s ease;
        }
        
        .card:hover {
            transform: translateY(-2px);
        }
        
        .btn-discord {
            background: var(--discord-blurple);
            border: none;
            color: white;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        
        .btn-discord:hover {
            background: #4752C4;
            color: white;
            transform: translateY(-1px);
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
        }
        
        .activity-item {
            border-left: 4px solid var(--discord-blurple);
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 0 10px 10px 0;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid var(--discord-blurple);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .alert {
            border: none;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .table {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        
        .form-control, .form-select {
            border-radius: 8px;
            border: 2px solid #e9ecef;
            transition: border-color 0.3s ease;
        }
        
        .form-control:focus, .form-select:focus {
            border-color: var(--discord-blurple);
            box-shadow: 0 0 0 0.2rem rgba(88, 101, 242, 0.25);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="bi bi-robot"></i> Bot Discord
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    {% if session.logged_in %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('dashboard') }}"><i class="bi bi-speedometer2"></i> Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('economy') }}"><i class="bi bi-coin"></i> Économie</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('moderation') }}"><i class="bi bi-shield"></i> Modération</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('settings') }}"><i class="bi bi-gear"></i> Paramètres</a>
                    </li>
                    {% endif %}
                </ul>
                <ul class="navbar-nav">
                    {% if session.logged_in %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('logout') }}"><i class="bi bi-box-arrow-right"></i> Déconnexion</a>
                    </li>
                    {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('login') }}"><i class="bi bi-box-arrow-in-right"></i> Connexion</a>
                    </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        <i class="bi bi-{{ 'exclamation-triangle' if category == 'error' else 'check-circle' if category == 'success' else 'info-circle' }}"></i>
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Auto-refresh pour certaines pages
        if (window.location.pathname.includes('dashboard')) {
            setInterval(() => {
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('stats-container')?.innerHTML = updateStats(data);
                    })
                    .catch(console.error);
            }, 30000); // Refresh toutes les 30 secondes
        }
        
        function updateStats(data) {
            return `
                <div class="col-md-3">
                    <div class="card stat-card text-center p-3">
                        <h3>${data.guilds || 0}</h3>
                        <p class="mb-0">Serveurs</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card text-center p-3">
                        <h3>${data.users || 0}</h3>
                        <p class="mb-0">Utilisateurs</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card text-center p-3">
                        <h3>${data.commands_today || 0}</h3>
                        <p class="mb-0">Commandes aujourd'hui</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card text-center p-3">
                        <h3>${data.uptime || '0h'}</h3>
                        <p class="mb-0">Uptime</p>
                    </div>
                </div>
            `;
        }
        
        // Confirmation pour les actions destructives
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('btn-danger') || e.target.closest('.btn-danger')) {
                if (!confirm('Êtes-vous sûr de vouloir effectuer cette action ?')) {
                    e.preventDefault();
                }
            }
        });
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""

# LOGIN_TEMPLATE déplacé dans templates/login.html

DASHBOARD_TEMPLATE = """
{% extends base_template %}
{% block title %}Dashboard - Bot Discord{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1><i class="bi bi-speedometer2"></i> Dashboard</h1>
    <div class="badge bg-success fs-6">
        <i class="bi bi-circle-fill"></i> En ligne
    </div>
</div>

<div class="row mb-4" id="stats-container">
    <div class="col-md-3">
        <div class="card stat-card text-center p-3">
            <h3>{{ stats.guilds }}</h3>
            <p class="mb-0">Serveurs</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card text-center p-3">
            <h3>{{ stats.users }}</h3>
            <p class="mb-0">Utilisateurs</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card text-center p-3">
            <h3>{{ stats.commands_today }}</h3>
            <p class="mb-0">Commandes aujourd'hui</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card text-center p-3">
            <h3>{{ stats.uptime }}</h3>
            <p class="mb-0">Uptime</p>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5><i class="bi bi-activity"></i> Activité Récente</h5>
            </div>
            <div class="card-body">
                {% for activity in recent_activities %}
                <div class="activity-item">
                    <div class="d-flex justify-content-between">
                        <div>
                            <strong>{{ activity.action_type }}</strong>
                            <p class="mb-1 text-muted">{{ activity.description }}</p>
                        </div>
                        <small class="text-muted">{{ activity.timestamp }}</small>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="bi bi-gear"></i> Actions Rapides</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="{{ url_for('economy') }}" class="btn btn-outline-primary">
                        <i class="bi bi-coin"></i> Gérer l'Économie
                    </a>
                    <a href="{{ url_for('moderation') }}" class="btn btn-outline-warning">
                        <i class="bi bi-shield"></i> Modération
                    </a>
                    <a href="{{ url_for('settings') }}" class="btn btn-outline-secondary">
                        <i class="bi bi-gear"></i> Paramètres
                    </a>
                    <button class="btn btn-outline-info" onclick="refreshStats(this)">
                        <i class="bi bi-arrow-clockwise"></i> Actualiser
                    </button>
                </div>
            </div>
        </div>
        
        <div class="card mt-3">
            <div class="card-header">
                <h5><i class="bi bi-exclamation-triangle"></i> Alertes</h5>
            </div>
            <div class="card-body">
                {% if alerts %}
                    {% for alert in alerts %}
                    <div class="alert alert-{{ alert.type }} py-2 px-3">
                        {{ alert.message }}
                    </div>
                    {% endfor %}
                {% else %}
                <p class="text-muted mb-0">Aucune alerte</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function refreshStats(btn) {
    const button = btn || document.querySelector('button[onclick*="refreshStats"]');
    const originalText = button ? button.innerHTML : '';
    if (button) {
        button.innerHTML = '<span class="loading"></span> Actualisation...';
        button.disabled = true;
    }

    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('stats-container').innerHTML = updateStats(data);
        })
        .catch(error => {
            console.error('Erreur:', error);
        })
        .finally(() => {
            if (button) {
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                }, 500);
            }
        });
}
</script>
{% endblock %}
"""

# Décorateur pour vérifier l'authentification
def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return redirect(url_for('dashboard' if session.get('logged_in') else 'login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ip = request.remote_addr or 'unknown'
        if _login_is_rate_limited(ip):
            flash(f'Trop de tentatives. Réessayez dans {_LOGIN_WINDOW // 60} minutes.', 'error')
            logger.warning(f"Login rate-limited pour IP {ip}")
            return render_template('login.html')

        password = request.form.get('password', '')

        if check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            session['login_time'] = datetime.now().isoformat()
            flash('Connexion réussie !', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Mot de passe incorrect.', 'error')
            logger.warning(f"Tentative de connexion échouée depuis {ip}")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnexion réussie.', 'info')
    return redirect(url_for('login'))

def _format_uptime(delta):
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes = (remainder // 60)
    return f"{hours}h {minutes}m"

def _compute_stats() -> Dict[str, Any]:
    guilds = users = commands_today = 0
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(1) FROM guilds")
            row = cur.fetchone()
            guilds = row[0] if row and row[0] is not None else 0

            cur.execute("SELECT COUNT(1) FROM users")
            row = cur.fetchone()
            users = row[0] if row and row[0] is not None else 0

            cur.execute(
                "SELECT COUNT(1) FROM activity_logs WHERE action_type = ? AND date(timestamp) = date('now','localtime')",
                ("COMMAND_USED",)
            )
            row = cur.fetchone()
            commands_today = row[0] if row and row[0] is not None else 0
    except Exception as e:
        logger.error(f"Erreur calcul statistiques: {e}")
    uptime = _format_uptime(datetime.now() - START_TIME)
    return {'guilds': guilds, 'users': users, 'commands_today': commands_today, 'uptime': uptime}

def _get_recent_activities(limit: int = 10) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT action_type, action_data, timestamp FROM activity_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            for action_type, action_data, ts in cur.fetchall():
                items.append({
                    'action_type': action_type,
                    'description': action_data or '',
                    'timestamp': ts
                })
    except Exception as e:
        logger.error(f"Erreur récupération activités récentes: {e}")
    return items

@app.route('/dashboard')
@require_auth
def dashboard():
    # Récupérer les statistiques
    stats = {
        'guilds': 0,
        'users': 0,
        'commands_today': 0,
        'uptime': '0h'
    }
    
    recent_activities = []
    alerts = []
    
    try:
        stats = _compute_stats()
        recent_activities = _get_recent_activities(10)
        if stats['guilds'] == 0:
            alerts.append({'type': 'warning', 'message': "Le bot n'est connecté à aucun serveur"})
    except Exception as e:
        logger.error(f"Erreur récupération stats dashboard: {e}")
        alerts.append({'type': 'danger', 'message': 'Erreur de connexion à la base de données'})
    
    return render_template(
        'dashboard.html',
        stats=stats,
        recent_activities=recent_activities,
        alerts=alerts
    )

@app.route('/economy')
@require_auth
def economy():
    # Page de gestion de l'économie
    # Exemple de récupération des utilisateurs et stats
    users = []
    stats = {'total_coins': 0, 'user_count': 0}
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT username, coins, level FROM members LEFT JOIN users ON members.user_id = users.id")
            for username, coins, level in cur.fetchall():
                users.append({'username': username, 'coins': coins, 'level': level})
            cur.execute("SELECT SUM(coins) FROM members")
            row = cur.fetchone()
            stats['total_coins'] = row[0] if row and row[0] is not None else 0
            cur.execute("SELECT COUNT(DISTINCT user_id) FROM members")
            row = cur.fetchone()
            stats['user_count'] = row[0] if row and row[0] is not None else 0
    except Exception as e:
        logger.error(f"Erreur économie: {e}")
    return render_template('economy.html', users=users, stats=stats)

@app.route('/moderation')
@require_auth
def moderation():
    # Page de modération
    members = []
    stats = {'member_count': 0, 'banned_count': 0, 'muted_count': 0}
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT username, 'Membre' as role FROM users")
            for username, role in cur.fetchall():
                members.append({'username': username, 'role': role})
            cur.execute("SELECT COUNT(*) FROM users")
            row = cur.fetchone()
            stats['member_count'] = row[0] if row and row[0] is not None else 0
            cur.execute("SELECT COUNT(*) FROM members WHERE ban_reason IS NOT NULL")
            row = cur.fetchone()
            stats['banned_count'] = row[0] if row and row[0] is not None else 0
            cur.execute("SELECT COUNT(*) FROM members WHERE muted = 1")
            row = cur.fetchone()
            stats['muted_count'] = row[0] if row and row[0] is not None else 0
    except Exception as e:
        logger.error(f"Erreur modération: {e}")
    return render_template('moderation.html', members=members, stats=stats)

@app.route('/settings')
@require_auth
def settings():
    # Page de paramètres
    settings = {'prefix': '!', 'language': 'fr'}
    stats = {'guilds': 0, 'users': 0, 'uptime': '0h'}
    if request.method == 'POST':
        prefix = request.form.get('prefix', '!')
        language = request.form.get('language', 'fr')
        settings['prefix'] = prefix
        settings['language'] = language
        flash('Paramètres enregistrés.', 'success')
    try:
        stats = _compute_stats()
    except Exception as e:
        logger.error(f"Erreur stats settings: {e}")
    return render_template('settings.html', settings=settings, stats=stats)

@app.route('/api/stats')
@require_auth
def api_stats():
    """API pour récupérer les statistiques en temps réel"""
    try:
        stats = _compute_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Erreur API stats: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', code=404, message="Page non trouvée", description="La page que vous cherchez n'existe pas."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', code=500, message="Erreur interne", description="Une erreur s'est produite sur le serveur."), 500

def run_web_interface():
    """Lance l'interface web"""
    logger.info(f"🌐 Interface web démarrée sur http://{Config.INTERFACE_HOST}:{Config.INTERFACE_PORT}")
    app.run(
        host=Config.INTERFACE_HOST,
        port=Config.INTERFACE_PORT,
        debug=False,  # Jamais en debug en production
        threaded=True
    )

if __name__ == '__main__':
    run_web_interface()