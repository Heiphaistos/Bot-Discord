"""
Cog avec des utilitaires avancés et des commandes supplémentaires
"""
import random
import asyncio
import datetime
import base64
import json
import hashlib
from typing import Optional, List, Dict
import math

import discord
from discord import app_commands
from discord.ext import commands

from config import Config
from database import db_manager
from utils.logger import bot_logger
from utils.security import require_permissions, rate_limit, input_validator, SafeCalculator

class AdvancedUtilsCog(commands.Cog):
    """Utilitaires avancés et commandes diverses"""
    
    def __init__(self, bot):
        self.bot = bot
        
    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module utilitaires avancés chargé")

    # === COMMANDES DE TEXTE ET CONVERSION ===
    
    @app_commands.command(name="ascii", description="Convertit du texte en ASCII art simple")
    async def ascii_art(self, interaction: discord.Interaction, texte: str):
        """Convertit en ASCII art"""
        if len(texte) > 10:
            await interaction.response.send_message("❌ Texte trop long (10 caractères max).")
            return
            
        # ASCII art simple
        ascii_dict = {
            'A': ['  █  ', ' █ █ ', '█████', '█   █', '█   █'],
            'B': ['████ ', '█   █', '████ ', '█   █', '████ '],
            'C': [' ███ ', '█    ', '█    ', '█    ', ' ███ '],
            'D': ['████ ', '█   █', '█   █', '█   █', '████ '],
            'E': ['█████', '█    ', '███  ', '█    ', '█████'],
            'F': ['█████', '█    ', '███  ', '█    ', '█    '],
            'G': [' ███ ', '█    ', '█ ██ ', '█   █', ' ███ '],
            'H': ['█   █', '█   █', '█████', '█   █', '█   █'],
            'I': ['█████', '  █  ', '  █  ', '  █  ', '█████'],
            'J': ['█████', '   █ ', '   █ ', '█  █ ', ' ██  '],
            ' ': ['     ', '     ', '     ', '     ', '     '],
            '!': ['  █  ', '  █  ', '  █  ', '     ', '  █  ']
        }
        
        lines = ['', '', '', '', '']
        for char in texte.upper():
            if char in ascii_dict:
                for i in range(5):
                    lines[i] += ascii_dict[char][i] + ' '
            else:
                for i in range(5):
                    lines[i] += '█████ '
        
        result = '\n'.join(lines)
        
        embed = discord.Embed(
            title="🎨 ASCII Art",
            description=f"```\n{result}\n```",
            color=discord.Color.purple()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="base64", description="Encode/décode en Base64")
    async def base64_converter(self, interaction: discord.Interaction, action: str, texte: str):
        """Convertisseur Base64"""
        try:
            if action.lower() == "encode":
                result = base64.b64encode(texte.encode()).decode()
                title = "📤 Encodage Base64"
            elif action.lower() == "decode":
                result = base64.b64decode(texte).decode()
                title = "📥 Décodage Base64"
            else:
                await interaction.response.send_message("❌ Action invalide. Utilisez 'encode' ou 'decode'.")
                return
                
            embed = discord.Embed(title=title, color=discord.Color.blue())
            embed.add_field(name="Entrée", value=f"```{texte[:100]}```", inline=False)
            embed.add_field(name="Résultat", value=f"```{result[:100]}```", inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception:
            await interaction.response.send_message("❌ Erreur lors de la conversion.")

    @app_commands.command(name="hash", description="Génère un hash MD5/SHA256")
    async def hash_text(self, interaction: discord.Interaction, algorithme: str, texte: str):
        """Générateur de hash"""
        try:
            if algorithme.lower() == "md5":
                result = hashlib.md5(texte.encode()).hexdigest()
            elif algorithme.lower() == "sha256":
                result = hashlib.sha256(texte.encode()).hexdigest()
            else:
                await interaction.response.send_message("❌ Algorithme invalide. Utilisez 'md5' ou 'sha256'.")
                return
                
            embed = discord.Embed(
                title=f"🔒 Hash {algorithme.upper()}",
                color=discord.Color.dark_green()
            )
            embed.add_field(name="Texte original", value=f"```{texte[:50]}```", inline=False)
            embed.add_field(name="Hash", value=f"```{result}```", inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}")

    @app_commands.command(name="reverse", description="Inverse un texte")
    async def reverse_text(self, interaction: discord.Interaction, texte: str):
        """Inverse un texte"""
        reversed_text = texte[::-1]
        
        embed = discord.Embed(
            title="🔄 Texte inversé",
            color=discord.Color.blue()
        )
        embed.add_field(name="Original", value=texte, inline=False)
        embed.add_field(name="Inversé", value=reversed_text, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leet", description="Convertit en l33t speak")
    async def leet_speak(self, interaction: discord.Interaction, texte: str):
        """Convertit en l33t speak"""
        leet_dict = {
            'A': '4', 'E': '3', 'I': '1', 'O': '0', 'U': 'u',
            'S': '5', 'T': '7', 'L': '1', 'G': '6', 'B': '8'
        }
        
        leet_text = ''
        for char in texte:
            leet_text += leet_dict.get(char.upper(), char)
            
        embed = discord.Embed(
            title="💻 L33t Speak",
            color=discord.Color.green()
        )
        embed.add_field(name="Original", value=texte, inline=False)
        embed.add_field(name="L33t", value=leet_text, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="morse", description="Convertit en code Morse")
    async def morse_code(self, interaction: discord.Interaction, texte: str):
        """Convertit en code Morse"""
        morse_dict = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
            '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
            '8': '---..', '9': '----.', ' ': '/'
        }
        
        morse_text = ' '.join(morse_dict.get(char.upper(), '?') for char in texte)
        
        embed = discord.Embed(
            title="📡 Code Morse",
            color=discord.Color.orange()
        )
        embed.add_field(name="Original", value=texte, inline=False)
        embed.add_field(name="Morse", value=f"```{morse_text}```", inline=False)
        
        await interaction.response.send_message(embed=embed)

    # === GÉNÉRATEURS ET OUTILS ALÉATOIRES ===
    
    @app_commands.command(name="password", description="Génère un mot de passe sécurisé")
    async def generate_password(self, interaction: discord.Interaction, longueur: int = 12, complexite: str = "normale"):
        """Génère un mot de passe"""
        if longueur < 4 or longueur > 100:
            await interaction.response.send_message("❌ Longueur invalide (4-100 caractères).")
            return
            
        if complexite.lower() == "simple":
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        elif complexite.lower() == "normale":
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        elif complexite.lower() == "complexe":
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"
        else:
            await interaction.response.send_message("❌ Complexité invalide. Utilisez: simple, normale, complexe.")
            return
            
        password = ''.join(random.choice(chars) for _ in range(longueur))
        
        embed = discord.Embed(
            title="🔐 Mot de passe généré",
            description=f"```{password}```",
            color=discord.Color.dark_green()
        )
        embed.add_field(name="Longueur", value=longueur, inline=True)
        embed.add_field(name="Complexité", value=complexite.title(), inline=True)
        embed.set_footer(text="⚠️ Envoyé en privé pour votre sécurité")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="uuid", description="Génère un UUID")
    async def generate_uuid(self, interaction: discord.Interaction):
        """Génère un UUID"""
        import uuid
        generated_uuid = str(uuid.uuid4())
        
        embed = discord.Embed(
            title="🆔 UUID Généré",
            description=f"```{generated_uuid}```",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="color", description="Génère une couleur aléatoire")
    async def random_color(self, interaction: discord.Interaction):
        """Génère une couleur aléatoire"""
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        rgb_color = f"rgb({r}, {g}, {b})"
        
        embed = discord.Embed(
            title="🎨 Couleur Aléatoire",
            color=discord.Color.from_rgb(r, g, b)
        )
        embed.add_field(name="Hexadécimal", value=hex_color, inline=True)
        embed.add_field(name="RGB", value=rgb_color, inline=True)
        embed.add_field(name="Valeurs", value=f"R:{r} G:{g} B:{b}", inline=True)
        
        await interaction.response.send_message(embed=embed)

    # === CALCULS ET CONVERSIONS ===
    
    @app_commands.command(name="convert_temp", description="Convertit une température")
    async def convert_temperature(self, interaction: discord.Interaction, temperature: float, unite_source: str, unite_cible: str):
        """Convertisseur de température"""
        units = ["celsius", "fahrenheit", "kelvin", "c", "f", "k"]
        
        if unite_source.lower() not in units or unite_cible.lower() not in units:
            await interaction.response.send_message("❌ Unités invalides. Utilisez: celsius/c, fahrenheit/f, kelvin/k")
            return
            
        # Normaliser les unités
        source = unite_source.lower()
        if source in ["celsius", "c"]:
            source = "c"
        elif source in ["fahrenheit", "f"]:
            source = "f"
        elif source in ["kelvin", "k"]:
            source = "k"
            
        cible = unite_cible.lower()
        if cible in ["celsius", "c"]:
            cible = "c"
        elif cible in ["fahrenheit", "f"]:
            cible = "f"
        elif cible in ["kelvin", "k"]:
            cible = "k"
        
        # Convertir en Celsius d'abord
        if source == "c":
            celsius = temperature
        elif source == "f":
            celsius = (temperature - 32) * 5/9
        elif source == "k":
            celsius = temperature - 273.15
            
        # Convertir vers l'unité cible
        if cible == "c":
            result = celsius
        elif cible == "f":
            result = celsius * 9/5 + 32
        elif cible == "k":
            result = celsius + 273.15
            
        unit_names = {"c": "Celsius", "f": "Fahrenheit", "k": "Kelvin"}
        
        embed = discord.Embed(
            title="🌡️ Conversion de Température",
            color=discord.Color.red()
        )
        embed.add_field(name="Source", value=f"{temperature}° {unit_names[source]}", inline=True)
        embed.add_field(name="Résultat", value=f"{result:.2f}° {unit_names[cible]}", inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="calculate_age", description="Calcule l'âge à partir d'une date de naissance")
    async def calculate_age(self, interaction: discord.Interaction, annee: int, mois: int, jour: int):
        """Calcule l'âge"""
        try:
            birth_date = datetime.date(annee, mois, jour)
            today = datetime.date.today()
            
            if birth_date > today:
                await interaction.response.send_message("❌ Date de naissance dans le futur !")
                return
                
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            days_lived = (today - birth_date).days
            
            # Prochain anniversaire
            next_birthday = datetime.date(today.year, birth_date.month, birth_date.day)
            if next_birthday < today:
                next_birthday = datetime.date(today.year + 1, birth_date.month, birth_date.day)
            days_until_birthday = (next_birthday - today).days
            
            embed = discord.Embed(
                title="🎂 Calculateur d'Âge",
                color=discord.Color.gold()
            )
            embed.add_field(name="Âge", value=f"{age} ans", inline=True)
            embed.add_field(name="Jours vécus", value=f"{days_lived:,}", inline=True)
            embed.add_field(name="Prochain anniversaire", value=f"Dans {days_until_birthday} jours", inline=True)
            embed.add_field(name="Date de naissance", value=birth_date.strftime("%d/%m/%Y"), inline=True)
            
            # Fun facts
            hours_lived = days_lived * 24
            minutes_lived = hours_lived * 60
            embed.add_field(name="Heures vécues", value=f"{hours_lived:,}", inline=True)
            embed.add_field(name="Minutes vécues", value=f"{minutes_lived:,}", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            await interaction.response.send_message("❌ Date invalide !")

    @app_commands.command(name="math", description="Résout une expression mathématique avancée")
    async def advanced_math(self, interaction: discord.Interaction, expression: str):
        """Calculateur mathématique avancé"""
        try:
            # Remplacer les fonctions communes
            expression = expression.replace("^", "**")

            result = SafeCalculator.safe_eval(expression)

            embed = discord.Embed(
                title="🔢 Calculateur Avancé",
                color=discord.Color.green()
            )
            embed.add_field(name="Expression", value=f"```{expression}```", inline=False)
            embed.add_field(name="Résultat", value=f"**{result}**", inline=False)

            # Si c'est un float, montrer aussi la version arrondie
            if isinstance(result, float) and not result.is_integer():
                embed.add_field(name="Arrondi", value=f"≈ {round(result, 6)}", inline=True)

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur de calcul: {str(e)[:100]}")

    # === OUTILS DE TEMPS ===
    
    @app_commands.command(name="timestamp", description="Génère un timestamp Discord")
    async def timestamp_generator(self, interaction: discord.Interaction, format_type: str = "f"):
        """Générateur de timestamp Discord"""
        now = int(datetime.datetime.now().timestamp())
        
        formats = {
            "t": "Heure courte (16:20)",
            "T": "Heure longue (16:20:30)", 
            "d": "Date courte (20/04/2021)",
            "D": "Date longue (20 avril 2021)",
            "f": "Date et heure courtes (20 avril 2021 16:20)",
            "F": "Date et heure longues (mardi 20 avril 2021 16:20)",
            "R": "Relatif (il y a 2 mois)"
        }
        
        if format_type.lower() not in formats:
            format_list = '\n'.join(f"`{k}`: {v}" for k, v in formats.items())
            await interaction.response.send_message(f"❌ Format invalide. Formats disponibles:\n{format_list}")
            return
            
        timestamp = f"<t:{now}:{format_type}>"
        
        embed = discord.Embed(
            title="⏰ Générateur de Timestamp",
            color=discord.Color.blue()
        )
        embed.add_field(name="Code", value=f"`<t:{now}:{format_type}>`", inline=False)
        embed.add_field(name="Aperçu", value=timestamp, inline=False)
        embed.add_field(name="Format", value=formats[format_type], inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="countdown", description="Lance un compte à rebours")
    async def countdown(self, interaction: discord.Interaction, secondes: int):
        """Compte à rebours"""
        if secondes <= 0 or secondes > 300:  # Max 5 minutes
            await interaction.response.send_message("❌ Durée invalide (1-300 secondes).")
            return
            
        await interaction.response.send_message(f"⏰ Compte à rebours de {secondes} secondes lancé !")
        
        # Afficher seulement les 10 dernières secondes
        for i in range(secondes, 0, -1):
            if i <= 10:
                try:
                    embed = discord.Embed(
                        title="⏰ Compte à Rebours",
                        description=f"**{i}**",
                        color=discord.Color.orange() if i > 3 else discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed)
                    if i > 1:
                        await asyncio.sleep(1)
                except:
                    break
            else:
                await asyncio.sleep(1)
                
        try:
            embed = discord.Embed(
                title="🎉 TEMPS ÉCOULÉ !",
                description="Le compte à rebours est terminé !",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
        except:
            pass

    # === OUTILS D'ANALYSE ===
    
    @app_commands.command(name="analyze_text", description="Analyse un texte")
    async def analyze_text(self, interaction: discord.Interaction, texte: str):
        """Analyse un texte"""
        # Statistiques de base
        char_count = len(texte)
        word_count = len(texte.split())
        line_count = texte.count('\n') + 1
        
        # Caractères uniques
        unique_chars = len(set(texte.lower()))
        
        # Mots les plus fréquents
        words = texte.lower().split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        most_common = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        embed = discord.Embed(
            title="📊 Analyse de Texte",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="📝 Caractères", value=char_count, inline=True)
        embed.add_field(name="📖 Mots", value=word_count, inline=True)
        embed.add_field(name="📄 Lignes", value=line_count, inline=True)
        embed.add_field(name="🔤 Caractères uniques", value=unique_chars, inline=True)
        
        if most_common:
            common_words = '\n'.join(f"{word}: {count}" for word, count in most_common)
            embed.add_field(name="🔥 Mots fréquents", value=f"```{common_words}```", inline=False)
            
        # Aperçu du texte
        preview = texte[:100] + ('...' if len(texte) > 100 else '')
        embed.add_field(name="👀 Aperçu", value=f"```{preview}```", inline=False)
        
        await interaction.response.send_message(embed=embed)

    # === OUTILS DIVERS ===
    
    @app_commands.command(name="qrcode", description="Génère un lien QR code")
    async def qr_code(self, interaction: discord.Interaction, texte: str):
        """Génère un QR code (lien)"""
        import urllib.parse
        
        encoded_text = urllib.parse.quote(texte)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_text}"
        
        embed = discord.Embed(
            title="📱 QR Code",
            description=f"QR Code pour: `{texte[:50]}{'...' if len(texte) > 50 else ''}`",
            color=discord.Color.dark_blue()
        )
        embed.set_image(url=qr_url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="flip", description="Lance une pièce")
    async def flip_coin(self, interaction: discord.Interaction, nombre: int = 1):
        """Lance une ou plusieurs pièces"""
        if nombre <= 0 or nombre > 50:
            await interaction.response.send_message("❌ Nombre invalide (1-50 pièces).")
            return
            
        results = [random.choice(["Pile", "Face"]) for _ in range(nombre)]
        
        if nombre == 1:
            result = results[0]
            emoji = "🪙" if result == "Pile" else "🎯"
            
            embed = discord.Embed(
                title="🪙 Lancer de Pièce",
                description=f"{emoji} **{result}** !",
                color=discord.Color.gold()
            )
        else:
            pile_count = results.count("Pile")
            face_count = results.count("Face")
            
            embed = discord.Embed(
                title=f"🪙 {nombre} Lancers de Pièce",
                color=discord.Color.gold()
            )
            embed.add_field(name="🪙 Pile", value=pile_count, inline=True)
            embed.add_field(name="🎯 Face", value=face_count, inline=True)
            embed.add_field(name="📊 Ratio", value=f"{pile_count/nombre:.1%} Pile", inline=True)
            
            if nombre <= 10:
                result_str = ' '.join("🪙" if r == "Pile" else "🎯" for r in results)
                embed.add_field(name="Résultats", value=result_str, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="random_choice", description="Fait un choix aléatoire")
    async def random_choice(self, interaction: discord.Interaction, options: str):
        """Fait un choix aléatoire parmi les options"""
        choices = [choice.strip() for choice in options.split(',') if choice.strip()]
        
        if len(choices) < 2:
            await interaction.response.send_message("❌ Donnez au moins 2 options séparées par des virgules.")
            return
            
        if len(choices) > 20:
            await interaction.response.send_message("❌ Trop d'options (20 max).")
            return
            
        chosen = random.choice(choices)
        
        embed = discord.Embed(
            title="🎯 Choix Aléatoire",
            description=f"**{chosen}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Options", value=f"{len(choices)} disponibles", inline=True)
        embed.add_field(name="Choisi", value=chosen, inline=True)
        
        if len(choices) <= 10:
            embed.add_field(name="Toutes les options", value=', '.join(choices), inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AdvancedUtilsCog(bot))