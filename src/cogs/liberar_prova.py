import discord
from discord.ext import commands
from discord import app_commands

class LiberarProva(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="liberar-prova", description="Libera a prova para um candidato")
    @app_commands.describe(membro="Membro que terá a prova liberada")
    async def liberar_prova(self, interaction: discord.Interaction, membro: discord.Member):
        await interaction.response.send_message(
            f"Liberação de prova para {membro.mention} será implementada em breve.",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(LiberarProva(bot))