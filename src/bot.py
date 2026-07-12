import discord 
from discord.ext import commands
import logging

from src.config import DISCORD_TOKEN, GUILD_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recrutamento-bot")

intents = discord.Intents.default()
intents.members = True

class RecrutamentoBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Carregar extensões (cogs)
        await self.load_extension("src.cogs.recrutar")
        await self.load_extension("src.cogs.liberar_prova")
        await self.load_extension("src.cogs.aprovar")
        await self.load_extension("src.cogs.reprovar")

        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        logger.info(f"Comandos de barra sincronizados com o servidor (ID: {GUILD_ID})")

    async def on_ready(self):
        logger.info(f"Bot conectado como {self.user} (ID: {self.user.id})")
        guild = self.get_guild(int(GUILD_ID))
        if guild:
            logger.info(f"Conectado ao servidor: {guild.name} (ID: {guild.id})")
        else:
            logger.warning("Não foi possível encontrar o servidor com o ID fornecido.")

bot = RecrutamentoBot()

def run():
    bot.run(DISCORD_TOKEN)