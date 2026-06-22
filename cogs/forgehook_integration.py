"""
Intégration ForgeHook — Utilise les webhooks et bots sauvegardés dans ForgeHook
depuis des commandes Discord.
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import aiohttp
import logging

from config import Config

logger = logging.getLogger(__name__)


class ForgeHookIntegration(commands.Cog):
    """Intégration avec ForgeHook (webhook manager self-hosted)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._session: Optional[aiohttp.ClientSession] = None

    async def cog_load(self):
        self._session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {Config.FORGEHOOK_API_TOKEN}"},
            timeout=aiohttp.ClientTimeout(total=10),
        )
        logger.info("Cog ForgeHook chargé")

    async def cog_unload(self):
        if self._session:
            await self._session.close()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _base(self) -> str:
        return Config.FORGEHOOK_URL.rstrip("/")

    async def _get(self, path: str):
        if not Config.FORGEHOOK_URL or not Config.FORGEHOOK_API_TOKEN:
            return None
        try:
            async with self._session.get(f"{self._base()}{path}") as r:
                if r.status == 200:
                    return await r.json()
        except Exception as e:
            logger.error(f"ForgeHook GET {path}: {e}")
        return None

    async def _post(self, path: str, payload: dict):
        if not Config.FORGEHOOK_URL or not Config.FORGEHOOK_API_TOKEN:
            return None
        try:
            async with self._session.post(f"{self._base()}{path}", json=payload) as r:
                return {"status": r.status, "data": await r.json()}
        except Exception as e:
            logger.error(f"ForgeHook POST {path}: {e}")
        return None

    # ── /forgehook group ──────────────────────────────────────────────────────

    fh = app_commands.Group(name="forgehook", description="Commandes ForgeHook")

    @fh.command(name="status", description="Statut de ForgeHook")
    async def fh_status(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not Config.FORGEHOOK_URL:
            return await interaction.followup.send("❌ ForgeHook non configuré (`FORGEHOOK_URL` manquant).", ephemeral=True)

        data = await self._get("/api/health") or await self._get("/health")
        if data:
            embed = discord.Embed(title="🪝 ForgeHook", color=discord.Color.green())
            embed.add_field(name="Statut", value="✅ En ligne", inline=True)
            embed.add_field(name="URL", value=Config.FORGEHOOK_URL, inline=True)
            if "version" in data:
                embed.add_field(name="Version", value=data["version"], inline=True)
        else:
            embed = discord.Embed(title="🪝 ForgeHook", color=discord.Color.red())
            embed.add_field(name="Statut", value="❌ Hors ligne ou inaccessible", inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @fh.command(name="webhooks", description="Liste les webhooks sauvegardés dans ForgeHook")
    async def fh_webhooks(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not Config.FORGEHOOK_URL:
            return await interaction.followup.send("❌ ForgeHook non configuré.", ephemeral=True)

        webhooks = await self._get("/api/webhooks")
        if webhooks is None:
            return await interaction.followup.send("❌ Impossible de joindre ForgeHook.", ephemeral=True)
        if not webhooks:
            return await interaction.followup.send("Aucun webhook enregistré dans ForgeHook.", ephemeral=True)

        embed = discord.Embed(title="🔗 Webhooks ForgeHook", color=discord.Color.blurple())
        for wh in webhooks[:20]:
            embed.add_field(
                name=f"#{wh['id']} — {wh['name']}",
                value=wh.get("category") or "Aucune catégorie",
                inline=True,
            )
        if len(webhooks) > 20:
            embed.set_footer(text=f"+ {len(webhooks) - 20} autres")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @fh.command(name="send", description="Envoie un message via un webhook ForgeHook")
    @app_commands.describe(
        webhook_id="ID du webhook ForgeHook",
        message="Message à envoyer",
        titre="Titre de l'embed (optionnel)",
    )
    async def fh_send(
        self,
        interaction: discord.Interaction,
        webhook_id: int,
        message: str,
        titre: Optional[str] = None,
    ):
        await interaction.response.defer(ephemeral=True)
        if not Config.FORGEHOOK_URL:
            return await interaction.followup.send("❌ ForgeHook non configuré.", ephemeral=True)

        if titre:
            payload = {
                "embeds": [{
                    "title": titre,
                    "description": message,
                    "color": 0x5865F2,
                    "footer": {"text": f"Envoyé par {interaction.user.display_name} via Bot Discord"},
                }]
            }
        else:
            payload = {"content": message}

        result = await self._post("/api/discord/send", {"webhook_id": webhook_id, "payload": payload})
        if result and result["status"] < 300:
            await interaction.followup.send("✅ Message envoyé via ForgeHook.", ephemeral=True)
        else:
            err = result["data"].get("error", "Erreur inconnue") if result else "Impossible de joindre ForgeHook"
            await interaction.followup.send(f"❌ Échec : {err}", ephemeral=True)

    @fh.command(name="templates", description="Liste les templates embed ForgeHook")
    async def fh_templates(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not Config.FORGEHOOK_URL:
            return await interaction.followup.send("❌ ForgeHook non configuré.", ephemeral=True)

        templates = await self._get("/api/templates")
        if templates is None:
            return await interaction.followup.send("❌ Impossible de joindre ForgeHook.", ephemeral=True)
        if not templates:
            return await interaction.followup.send("Aucun template enregistré.", ephemeral=True)

        embed = discord.Embed(title="📋 Templates ForgeHook", color=discord.Color.blurple())
        for tpl in templates[:15]:
            embed.add_field(name=tpl["name"], value=tpl.get("category") or "—", inline=True)
        if len(templates) > 15:
            embed.set_footer(text=f"+ {len(templates) - 15} autres · Voir forgehook.heiphaistos.org/templates")
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    if not Config.FORGEHOOK_URL:
        logger.warning("FORGEHOOK_URL non défini — cog ForgeHook désactivé")
        return
    await bot.add_cog(ForgeHookIntegration(bot))
