import discord
from discord import app_commands
from discord.ext import commands

from core.backup_manager import BackupManager
from core.diff_engine import DiffEngine
from utils.permissions import is_authorized


class DiffCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bm = BackupManager()
        self.de = DiffEngine()

    @app_commands.command(name="diff", description="Compara um backup com o estado atual do servidor")
    @app_commands.describe(arquivo="Nome do arquivo de backup (deixe vazio para usar o mais recente)")
    @is_authorized()
    async def diff(self, interaction: discord.Interaction, arquivo: str = None):
        await interaction.response.defer(thinking=True, ephemeral=True)

        filename = arquivo or self.bm.latest_backup_filename(interaction.guild.id)
        if not filename:
            await interaction.followup.send("Nenhum backup encontrado para comparar.")
            return

        backup = self.bm.load_backup(interaction.guild.id, filename)
        if not backup:
            await interaction.followup.send("Backup não encontrado.")
            return

        diff = self.de.compare(interaction.guild, backup)
        summary = self.de.summarize(diff)

        embed = discord.Embed(
            title=f"🔍 Comparação com: {filename}",
            description=summary,
            color=discord.Color.orange(),
        )
        embed.set_footer(text="Use /restore para aplicar as correções necessárias.")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(DiffCog(bot))
