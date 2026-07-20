import os
import discord
from discord import app_commands
from discord.ext import commands

from src.config import AUTO_BACKUP_INTERVAL_HOURS, MAX_BACKUPS_PER_GUILD, LOG_CHANNEL_NAME, BACKUP_DIR
from src.core.backup_manager import BackupManager


class StatusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bm = BackupManager()

    @app_commands.command(name="status", description="Mostra o status do sistema de backup")
    async def status(self, interaction: discord.Interaction):
        files = self.bm.list_backups(interaction.guild.id)
        latest = files[0] if files else "Nenhum"

        guild_dir = os.path.join(BACKUP_DIR, str(interaction.guild.id))
        total_size = 0
        if os.path.isdir(guild_dir):
            total_size = sum(
                os.path.getsize(os.path.join(guild_dir, f)) for f in os.listdir(guild_dir)
            )

        embed = discord.Embed(title="📊 Status do sistema de backup", color=discord.Color.blurple())
        embed.add_field(name="Backups salvos", value=str(len(files)))
        embed.add_field(name="Último backup", value=latest, inline=False)
        embed.add_field(name="Espaço usado", value=f"{total_size / 1024:.1f} KB")
        embed.add_field(name="Intervalo automático", value=f"A cada {AUTO_BACKUP_INTERVAL_HOURS}h")
        embed.add_field(name="Máx. backups guardados", value=str(MAX_BACKUPS_PER_GUILD))
        embed.add_field(name="Canal de logs", value=f"#{LOG_CHANNEL_NAME}")

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(StatusCog(bot))
