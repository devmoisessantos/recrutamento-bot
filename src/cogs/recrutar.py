import discord 
from discord.ext import commands
from discord import app_commands

class Recrutar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="recrutar", description="Iniciar recrutamento de um membro para o servidor.")
    @app_commands.describe(member="Membro a ser recrutado.")
    async def recrutar(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(
            f"Recrutando {member.mention} para o servidor!", 
            ephemeral=True
        )
async def setup(bot: commands.Bot):
    await bot.add_cog(Recrutar(bot))