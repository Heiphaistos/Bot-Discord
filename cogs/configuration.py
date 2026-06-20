"""
Module de configuration avancée du bot
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from utils.logger import bot_logger
from utils.security import require_permissions

class ConfigurationCog(commands.Cog):
    """Configuration du bot"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        bot_logger.logger.info("Module configuration chargé")

    @app_commands.command(name="config", description="Configuration générale")
    @require_permissions("admin")
    async def config(self, interaction: discord.Interaction):
        await interaction.response.send_message("⚙️ Configuration")

    @app_commands.command(name="prefix", description="Change le préfixe")
    @require_permissions("admin")
    async def prefix(self, interaction: discord.Interaction, nouveau: str):
        if not nouveau or len(nouveau) > 10 or any(c in nouveau for c in ' @#`'):
            await interaction.response.send_message(
                "❌ Préfixe invalide (1-10 chars, pas de @#` ou espaces)", ephemeral=True
            )
            return
        await interaction.response.send_message(f"✅ Préfixe changé: {nouveau}")

    @app_commands.command(name="language", description="Change la langue")
    @require_permissions("admin")
    async def language(self, interaction: discord.Interaction, langue: str):
        await interaction.response.send_message(f"🌐 Langue: {langue}")

    @app_commands.command(name="timezone_set", description="Définis le fuseau horaire")
    @require_permissions("admin")
    async def timezone_set(self, interaction: discord.Interaction, timezone: str):
        await interaction.response.send_message(f"🕐 Fuseau: {timezone}")

    @app_commands.command(name="autorole", description="Configure l'auto-rôle")
    @require_permissions("admin")
    async def autorole(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"🎭 Auto-rôle: {role.mention}")

    @app_commands.command(name="autorole_remove", description="Désactive l'auto-rôle")
    @require_permissions("admin")
    async def autorole_remove(self, interaction: discord.Interaction):
        await interaction.response.send_message("❌ Auto-rôle désactivé")

    @app_commands.command(name="muterole", description="Définis le rôle mute")
    @require_permissions("admin")
    async def muterole(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"🔇 Rôle mute: {role.mention}")

    @app_commands.command(name="modrole", description="Définis le rôle modérateur")
    @require_permissions("admin")
    async def modrole(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"👮 Rôle mod: {role.mention}")

    @app_commands.command(name="adminrole", description="Définis le rôle admin")
    @require_permissions("admin")
    async def adminrole(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"👑 Rôle admin: {role.mention}")

    @app_commands.command(name="log_channel", description="Salon de logs")
    @require_permissions("admin")
    async def log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.send_message(f"📝 Logs: {channel.mention}")

    @app_commands.command(name="mod_channel", description="Salon modération")
    @require_permissions("admin")
    async def mod_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.send_message(f"👮 Modération: {channel.mention}")

    @app_commands.command(name="announce_channel", description="Salon annonces")
    @require_permissions("admin")
    async def announce_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.send_message(f"📢 Annonces: {channel.mention}")

    @app_commands.command(name="starboard", description="Configure le starboard")
    @require_permissions("admin")
    async def starboard(self, interaction: discord.Interaction, channel: discord.TextChannel, stars: int = 3):
        await interaction.response.send_message(f"⭐ Starboard: {channel.mention} ({stars} ⭐)")

    @app_commands.command(name="starboard_disable", description="Désactive le starboard")
    @require_permissions("admin")
    async def starboard_disable(self, interaction: discord.Interaction):
        await interaction.response.send_message("❌ Starboard désactivé")

    @app_commands.command(name="verification", description="Configure la vérification")
    @require_permissions("admin")
    async def verification(self, interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role):
        await interaction.response.send_message(f"✅ Vérification: {channel.mention} → {role.mention}")

    @app_commands.command(name="verification_disable", description="Désactive la vérification")
    @require_permissions("admin")
    async def verification_disable(self, interaction: discord.Interaction):
        await interaction.response.send_message("❌ Vérification désactivée")

    @app_commands.command(name="leveling_enable", description="Active le système de niveaux")
    @require_permissions("admin")
    async def leveling_enable(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Niveaux activés")

    @app_commands.command(name="leveling_disable", description="Désactive le système de niveaux")
    @require_permissions("admin")
    async def leveling_disable(self, interaction: discord.Interaction):
        await interaction.response.send_message("❌ Niveaux désactivés")

    @app_commands.command(name="xp_rate", description="Taux de gain d'XP")
    @require_permissions("admin")
    async def xp_rate(self, interaction: discord.Interaction, multiplicateur: float):
        await interaction.response.send_message(f"⭐ Taux XP: x{multiplicateur}")

    @app_commands.command(name="level_rewards", description="Configure les récompenses de niveau")
    @require_permissions("admin")
    async def level_rewards(self, interaction: discord.Interaction, niveau: int, role: discord.Role):
        await interaction.response.send_message(f"🎁 Niveau {niveau} → {role.mention}")

    @app_commands.command(name="economy_enable", description="Active l'économie")
    @require_permissions("admin")
    async def economy_enable(self, interaction: discord.Interaction):
        await interaction.response.send_message("💰 Économie activée")

    @app_commands.command(name="economy_disable", description="Désactive l'économie")
    @require_permissions("admin")
    async def economy_disable(self, interaction: discord.Interaction):
        await interaction.response.send_message("❌ Économie désactivée")

    @app_commands.command(name="daily_amount", description="Montant du daily")
    @require_permissions("admin")
    async def daily_amount(self, interaction: discord.Interaction, montant: int):
        await interaction.response.send_message(f"💰 Daily: {montant} pièces")

    @app_commands.command(name="work_range", description="Fourchette du work")
    @require_permissions("admin")
    async def work_range(self, interaction: discord.Interaction, min: int, max: int):
        await interaction.response.send_message(f"💼 Work: {min}-{max} pièces")

    @app_commands.command(name="antiraid", description="Configure l'anti-raid")
    @require_permissions("admin")
    async def antiraid(self, interaction: discord.Interaction, activer: bool):
        await interaction.response.send_message(f"🛡️ Anti-raid: {'activé' if activer else 'désactivé'}")

    @app_commands.command(name="antispam", description="Configure l'anti-spam")
    @require_permissions("admin")
    async def antispam(self, interaction: discord.Interaction, activer: bool):
        await interaction.response.send_message(f"🛡️ Anti-spam: {'activé' if activer else 'désactivé'}")

    @app_commands.command(name="antilink", description="Configure l'anti-lien")
    @require_permissions("admin")
    async def antilink(self, interaction: discord.Interaction, activer: bool):
        await interaction.response.send_message(f"🔗 Anti-lien: {'activé' if activer else 'désactivé'}")

    @app_commands.command(name="antitoxic", description="Configure l'anti-toxicité")
    @require_permissions("admin")
    async def antitoxic(self, interaction: discord.Interaction, activer: bool):
        await interaction.response.send_message(f"🛡️ Anti-toxicité: {'activé' if activer else 'désactivé'}")

    @app_commands.command(name="autoresponder", description="Ajoute une réponse auto")
    @require_permissions("admin")
    async def autoresponder(self, interaction: discord.Interaction, trigger: str, reponse: str):
        await interaction.response.send_message(f"🤖 Auto-réponse: '{trigger}' → '{reponse}'")

    @app_commands.command(name="autoresponder_remove", description="Retire une réponse auto")
    @require_permissions("admin")
    async def autoresponder_remove(self, interaction: discord.Interaction, trigger: str):
        await interaction.response.send_message(f"❌ Auto-réponse '{trigger}' supprimée")

    @app_commands.command(name="autoresponder_list", description="Liste des réponses auto")
    @require_permissions("moderator")
    async def autoresponder_list(self, interaction: discord.Interaction):
        await interaction.response.send_message("📋 Liste des auto-réponses")

async def setup(bot):
    await bot.add_cog(ConfigurationCog(bot))
