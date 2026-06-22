"""
Commandes d'information pour le bot Discord
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime

from utils.logger import bot_logger

class InfoCog(commands.Cog):
    """Commandes d'information sur les utilisateurs, serveurs, etc."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module info chargé")

    @app_commands.command(name="userinfo", description="Affiche les informations d'un utilisateur")
    async def userinfo(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        """Informations sur un utilisateur"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        target = membre or interaction.user

        embed = discord.Embed(
            title=f"👤 Informations sur {target}",
            color=target.color if target.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.now()
        )

        embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)

        # Informations générales
        embed.add_field(name="🆔 ID", value=target.id, inline=True)
        embed.add_field(name="📛 Pseudo", value=target.nick or "Aucun", inline=True)
        embed.add_field(name="🤖 Bot", value="Oui" if target.bot else "Non", inline=True)

        # Dates
        embed.add_field(
            name="📅 Compte créé",
            value=discord.utils.format_dt(target.created_at, 'F') + f"\n({discord.utils.format_dt(target.created_at, 'R')})",
            inline=True
        )
        embed.add_field(
            name="📅 A rejoint",
            value=discord.utils.format_dt(target.joined_at, 'F') + f"\n({discord.utils.format_dt(target.joined_at, 'R')})",
            inline=True
        )

        # Rôles
        roles = [role.mention for role in target.roles[1:]]  # Exclure @everyone
        if roles:
            roles_text = ", ".join(roles[:10])
            if len(roles) > 10:
                roles_text += f" ... et {len(roles) - 10} autre(s)"
            embed.add_field(
                name=f"🎭 Rôles ({len(roles)})",
                value=roles_text,
                inline=False
            )

        # Permissions clés
        key_perms = []
        if target.guild_permissions.administrator:
            key_perms.append("Administrateur")
        if target.guild_permissions.manage_guild:
            key_perms.append("Gérer le serveur")
        if target.guild_permissions.manage_channels:
            key_perms.append("Gérer les canaux")
        if target.guild_permissions.manage_roles:
            key_perms.append("Gérer les rôles")
        if target.guild_permissions.kick_members:
            key_perms.append("Expulser des membres")
        if target.guild_permissions.ban_members:
            key_perms.append("Bannir des membres")

        if key_perms:
            embed.add_field(
                name="🔑 Permissions clés",
                value=", ".join(key_perms),
                inline=False
            )

        # Position dans la hiérarchie
        embed.add_field(name="📊 Position rôle", value=f"{target.top_role.mention} (position {target.top_role.position})", inline=True)

        # Statut
        status_emoji = {
            discord.Status.online: "🟢 En ligne",
            discord.Status.idle: "🟡 Inactif",
            discord.Status.dnd: "🔴 Ne pas déranger",
            discord.Status.offline: "⚫ Hors ligne"
        }
        embed.add_field(name="📡 Statut", value=status_emoji.get(target.status, "❓ Inconnu"), inline=True)

        embed.set_footer(text=f"Demandé par {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Affiche les informations du serveur")
    async def serverinfo(self, interaction: discord.Interaction):
        """Informations sur le serveur"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        guild = interaction.guild

        embed = discord.Embed(
            title=f"🏰 Informations sur {guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        # Informations générales
        embed.add_field(name="🆔 ID", value=guild.id, inline=True)
        embed.add_field(name="👑 Propriétaire", value=f"<@{guild.owner_id}>", inline=True)
        embed.add_field(name="📅 Créé le", value=discord.utils.format_dt(guild.created_at, 'F'), inline=True)

        # Statistiques
        total_members = guild.member_count
        bots = sum(1 for member in guild.members if member.bot)
        humans = total_members - bots

        embed.add_field(name="👥 Membres", value=f"Total: {total_members}\nHumains: {humans}\nBots: {bots}", inline=True)
        embed.add_field(name="📊 Canaux", value=f"Texte: {len(guild.text_channels)}\nVocal: {len(guild.voice_channels)}\nCatégories: {len(guild.categories)}", inline=True)
        embed.add_field(name="🎭 Rôles", value=len(guild.roles), inline=True)

        # Boosts
        embed.add_field(name="💎 Niveau de boost", value=f"Niveau {guild.premium_tier}\n{guild.premium_subscription_count} boosts", inline=True)

        # Emojis
        embed.add_field(name="😀 Emojis", value=f"{len(guild.emojis)}/{guild.emoji_limit}", inline=True)

        # Niveau de vérification
        verification_levels = {
            discord.VerificationLevel.none: "Aucune",
            discord.VerificationLevel.low: "Faible",
            discord.VerificationLevel.medium: "Moyenne",
            discord.VerificationLevel.high: "Élevée",
            discord.VerificationLevel.highest: "Très élevée"
        }
        embed.add_field(name="🔒 Vérification", value=verification_levels.get(guild.verification_level, "Inconnue"), inline=True)

        # Description
        if guild.description:
            embed.add_field(name="📝 Description", value=guild.description, inline=False)

        embed.set_footer(text=f"Demandé par {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roleinfo", description="Affiche les informations d'un rôle")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        """Informations sur un rôle"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🎭 Informations sur {role.name}",
            color=role.color if role.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.now()
        )

        # Informations générales
        embed.add_field(name="🆔 ID", value=role.id, inline=True)
        embed.add_field(name="🎨 Couleur", value=str(role.color), inline=True)
        embed.add_field(name="📊 Position", value=role.position, inline=True)

        embed.add_field(name="👥 Membres", value=len(role.members), inline=True)
        embed.add_field(name="📌 Mentionnable", value="Oui" if role.mentionable else "Non", inline=True)
        embed.add_field(name="🎯 Affiché séparément", value="Oui" if role.hoist else "Non", inline=True)

        embed.add_field(name="📅 Créé le", value=discord.utils.format_dt(role.created_at, 'F'), inline=False)

        # Permissions clés
        key_perms = []
        if role.permissions.administrator:
            key_perms.append("Administrateur")
        if role.permissions.manage_guild:
            key_perms.append("Gérer le serveur")
        if role.permissions.manage_channels:
            key_perms.append("Gérer les canaux")
        if role.permissions.manage_roles:
            key_perms.append("Gérer les rôles")
        if role.permissions.kick_members:
            key_perms.append("Expulser des membres")
        if role.permissions.ban_members:
            key_perms.append("Bannir des membres")
        if role.permissions.manage_messages:
            key_perms.append("Gérer les messages")

        if key_perms:
            embed.add_field(
                name="🔑 Permissions clés",
                value=", ".join(key_perms),
                inline=False
            )

        embed.set_footer(text=f"Demandé par {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar_user", description="Affiche l'avatar d'un utilisateur")
    async def avatar(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        """Affiche l'avatar d'un utilisateur"""
        target = membre or interaction.user

        embed = discord.Embed(
            title=f"🖼️ Avatar de {target}",
            color=discord.Color.blue()
        )

        avatar_url = target.avatar.url if target.avatar else target.default_avatar.url
        embed.set_image(url=avatar_url)
        embed.add_field(name="🔗 Lien", value=f"[Télécharger]({avatar_url})", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="channelinfo", description="Affiche les informations d'un canal")
    async def channelinfo(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """Informations sur un canal"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        target_channel = channel or interaction.channel

        embed = discord.Embed(
            title=f"📝 Informations sur #{target_channel.name}",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        embed.add_field(name="🆔 ID", value=target_channel.id, inline=True)
        embed.add_field(name="🔖 Type", value=str(target_channel.type), inline=True)
        embed.add_field(name="📊 Position", value=target_channel.position, inline=True)

        if target_channel.category:
            embed.add_field(name="📁 Catégorie", value=target_channel.category.name, inline=True)

        embed.add_field(name="📅 Créé le", value=discord.utils.format_dt(target_channel.created_at, 'F'), inline=False)

        if target_channel.topic:
            embed.add_field(name="📝 Sujet", value=target_channel.topic[:1024], inline=False)

        embed.add_field(name="🔞 NSFW", value="Oui" if target_channel.is_nsfw() else "Non", inline=True)

        if hasattr(target_channel, 'slowmode_delay') and target_channel.slowmode_delay > 0:
            embed.add_field(name="⏱️ Mode lent", value=f"{target_channel.slowmode_delay}s", inline=True)

        embed.set_footer(text=f"Demandé par {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(InfoCog(bot))
