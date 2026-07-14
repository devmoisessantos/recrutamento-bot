import discord
from discord.ext import commands
from discord import app_commands

class Reprovar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reprovar", description="Reprova um candidato no recrutamento")
    @app_commands.describe(membro="Membro a ser reprovado")
    async def reprovar(self, interaction: discord.Interaction, membro: discord.Member):
        await interaction.response.send_message(
            f"Reprovação de {membro.mention} será implementada em breve.",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Reprovar(bot))