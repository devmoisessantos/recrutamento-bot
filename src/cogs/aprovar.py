import discord
from discord.ext import commands
from discord import app_commands

class Aprovar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="aprovar", description="Aprova um candidato no recrutamento")
    @app_commands.describe(membro="Membro a ser aprovado")
    async def aprovar(self, interaction: discord.Interaction, membro: discord.Member):
        await interaction.response.send_message(
            f"Aprovação de {membro.mention} será implementada em breve.",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Aprovar(bot))